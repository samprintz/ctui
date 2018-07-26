const N3 = require('n3');
const fs = require('fs');
const program = require('commander');

const _contactFile = __dirname + '/contacts.n3';

const { DataFactory } = N3;
const store = N3.Store();
const { namedNode, blankNode, literal, defaultGraph, quad } = DataFactory;


program
  .version('0.1.0')
  .option('-s, --show', 'Show all contacts')
  .option('-a, --add [name]', 'Add contact')
  .option('-r, --remove [name]', 'Remove contact')
  .option('-n, --name [name]', 'Show contact')
  .option('-g, --gift [gift]', 'Add gift idea for contact')
  .parse(process.argv);



if (program.show) {

  // read contacts into store
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      printContacts();
    }
  });

}



if (program.add) {

  // create new contact
  var newContact = quad(
    blankNode(),
    namedNode('http://hiea.de/contact#givenName'),
    literal(program.add),
    defaultGraph(),
  );

  // read contacts into store and add new contact
  debugger;
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  debugger;
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      const contactAlreadyExists = store.getQuads(null, null, literal(program.add))[0];
      if (!contactAlreadyExists) {
        store.addQuad(newContact);
        console.log('„%s“ added.', program.add);
        saveContacts();
      } else {
        console.log('„%s“ already exists.', program.add);
      }
    }
  });

}



if (program.remove) {

  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      const removedContact = store.getQuads(null, null, literal(program.remove))[0];
      if (removedContact) {
        store.forEach(function(gift) { // remove also associated gifts
          store.removeQuad(gift);
        }, removedContact.subject, namedNode('http://hiea.de/contact#giftIdea'), null);
        store.removeQuad(removedContact);
        console.log('Delete:');
        printContact(removedContact);
        saveContacts();
      } else {
        console.log('„%s“ doesn\'t exist.', program.remove);
      }
    }
  });
}



if (program.gift) {
  // name provided?
  if ({}.toString.call(program.name) === '[object Function]'){
    console.log('Please provide also a contact name.');
  } else {

  // get contacts
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
    debugger;
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      var contact = store.getQuads(null, null, literal(program.name))[0];
      if (!contact) {
        contact = DataFactory.quad(
          blankNode(),
          namedNode('http://hiea.de/contact#givenName'),
          literal(program.name),
          defaultGraph(),
        );
        store.addQuad(contact);
        console.log('„%s“ added.', program.name);
      }
      gift = DataFactory.quad(
        contact.subject,
        namedNode('http://hiea.de/contact#giftIdea'),
        literal(program.gift),
        defaultGraph(),
      );
      store.addQuad(gift);
      saveContacts();
      console.log('Add „' + program.gift + '“ as gift for „' + program.name + '“.');
    }
  });

  }

}



function saveContacts() {
  const writeStream = fs.createWriteStream(_contactFile);
  const writer = N3.Writer(writeStream, { end: false, prefixes: { c: 'http://hiea.de/contact#' } });

  // set new blank node prefixes (otherwise concats endless b0_)
  store.getSubjects().forEach(function(subject) {
    var blankNodeId = store.createBlankNode(); // set unused blank node identifier
    store.getQuads(subject, null, null).forEach(function(quad) {
      quad.subject = blankNodeId;
      // write
      writer.addQuad(quad);
    });
  });
  writer.end();
}

function printContact(contact) {
  // name
  console.log(contact.object.value);

  // gifts
  var giftString = "";
  store.forEach(function(gift) {
    giftString += gift.object.value + ", ";
  }, contact.subject, namedNode('http://hiea.de/contact#giftIdea'), null);
  if (giftString != "") {
    console.log("- gifts: " + giftString.substring(0, giftString.length - 2));
  }
}

function printContacts() {
  store.forEach(function(contact) {
    printContact(contact);
    console.log('\r');
  }, null, namedNode('http://hiea.de/contact#givenName'), null);
}

const N3 = require('n3');
const fs = require('fs');
const program = require('commander');

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
  const rdfStream = fs.createReadStream('out.n3');
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      console.log('Contacts:');
      printContacts();
    }
  });

}



if (program.add) {

  // create new contact
  var newContact = quad(
    blankNode(),
    namedNode('http://xmlns.com/foaf/0.1/givenName'),
    literal(program.add),
    defaultGraph(),
  );

  // read contacts into store and add new contact
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream('out.n3');
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
  const rdfStream = fs.createReadStream('out.n3');
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      const removedContact = store.getQuads(null, null, literal(program.remove))[0];
      if (removedContact) {
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

  // initialize contact and gift
  

  // get contacts
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream('out.n3');
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      var contact = store.getQuads(null, null, literal(program.name))[0];
      if (!contact) {
        contact = DataFactory.quad(
          blankNode(),
          namedNode('http://xmlns.com/foaf/0.1/givenName'),
          literal(program.name),
//TODO Überschreibt! Array/Liste/„komplexe“ Node?
          defaultGraph(),
        );
        store.addQuad(contact);
        console.log('„%s“ added.', program.name);
      }
      gift = DataFactory.quad(
        contact.subject,
        namedNode('http://xmlns.com/foaf/0.1/giftIdea'),
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
  const writeStream = fs.createWriteStream('out.n3');
  const writer = N3.Writer(writeStream, { end: false, prefixes: { c: 'http://example.org/cartoons#' } });
  store.forEach(quad => writer.addQuad(quad));
  writer.end();
}

function printContact(contact) {
  var name = contact.object.value;
  console.log(name);
}

function printContacts() {
  store.forEach(quad => printContact(quad));
}

const N3 = require('n3');
const fs = require('fs');
const program = require('commander');

const _contactFile = __dirname + '/contacts.n3';

const { DataFactory } = N3;
const store = N3.Store();
const { namedNode, blankNode, literal, defaultGraph, quad } = DataFactory;


program
  .version('0.1.0')
  .option('-s, --show [name]', 'Show contact. If no name specified, show all contacts.')
  .option('-a, --add [name]', 'Add contact')
  .option('-r, --remove [name]', 'Remove contact')
  .option('-n, --name [name]', 'Show contact')
  .option('-g, --add-gift [gift]', 'Add gift idea for contact (requires -n)')
  .option('-b, --add-birthday [date]', 'Add birthday for contact (requires -n)')
  .option('--rm-birthday', 'Remove birthday for contact (requires -n)')
  .option('--rm-gift [gift]', 'Remove gift idea for contact (requires -n)')
  .option('--gifted [occassion]', 'Mark gift as gifted and note occassion. (requires -g and -n)')
  .option('-e, --add-email [email]', 'Add email for contact (requires -n)')
  .option('--rm-email [email]', 'Remove email for contact (requires -n)')
  .option('-p, --add-phone [phone]', 'Add phone number for contact (requires -n)')
  .option('--rm-phone [phone]', 'Remove phone number for contact (requires -n)')
  .option('-t, --add-tag [tag]', 'Add tag for contact (requires -n)')
  .option('--rm-tag [tag]', 'Remove tag for contact (requires -n)')
  .parse(process.argv);



if (program.show) {

  // read contacts into store
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      if (typeof program.show === 'string') { // single contact
        const contact = store.getQuads(null, null, literal(program.show))[0];
			  // Suchfunktion gibt es bei Quads wohl nicht, kann aber in der Konsole mit | grep nach Personen suchen
        if (contact) {
          printContact(contact);
        } else {
          console.log('„%s“ doesn\'t exist.', program.show);
        }
      } else { // all contacts
        printContacts();
      }
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



if (program.addGift && program.gifted == null) { // prevent multiple actions, when gift is changed and -g specified
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
        literal(program.addGift),
        defaultGraph(),
      );
      store.addQuad(gift);
      saveContacts();
      console.log('Add „' + program.addGift + '“ as gift for ' + program.name + '.');
    }
  });

  }

}


if (program.addEmail) {
  // name provided?
  if ({}.toString.call(program.name) === '[object Function]'){
    console.log('Please provide also a contact name.');
  } else {
  // get contacts
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
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
      email = DataFactory.quad(
        contact.subject,
        namedNode('http://hiea.de/contact#email'),
        literal(program.addEmail),
        defaultGraph(),
      );
      store.addQuad(email);
      saveContacts();
      console.log('Add „' + program.addEmail + '“ as email for ' + program.name + '.');
    }
  });
  }
}



if (program.addPhone) {
  // name provided?
  if ({}.toString.call(program.name) === '[object Function]'){
    console.log('Please provide also a contact name.');
  } else {
  // get contacts
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
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
      tel = DataFactory.quad(
        contact.subject,
        namedNode('http://hiea.de/contact#tel'),
        literal(program.addPhone),
        defaultGraph(),
      );
      store.addQuad(tel);
      saveContacts();
      console.log('Add „' + program.addPhone + '“ as phone number for ' + program.name + '.');
    }
  });
  }
}



if (program.addBirthday) {
  // name provided?
  if ({}.toString.call(program.name) === '[object Function]'){
    console.log('Please provide also a contact name.');
  } else {
  // get contacts
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
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
      birthday = DataFactory.quad(
        contact.subject,
        namedNode('http://hiea.de/contact#birthday'),
        literal(program.addBirthday),
        defaultGraph(),
      );
      store.addQuad(birthday);
      saveContacts();
      console.log('Add ' + program.addBirthday + ' as birthday for ' + program.name + '.');
    }
  });
  }
}



if (program.addTag) {
  // name provided?
  if ({}.toString.call(program.name) === '[object Function]'){
    console.log('Please provide also a contact name.');
  } else {
  // get contacts
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
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
      tag = DataFactory.quad(
        contact.subject,
        namedNode('http://hiea.de/contact#tag'),
        literal(program.addTag),
        defaultGraph(),
      );
      store.addQuad(tag);
      saveContacts();
      console.log('' + program.name + ' tagged [' + program.addTag + '].');
    }
  });
  }
}


/* Manipulating attributes */

if (program.gifted) {
  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      var name = store.getQuads(null, namedNode('http://hiea.de/contact#givenName'), literal(program.name))[0];
      var gift = store.getQuads(null, namedNode('http://hiea.de/contact#giftIdea'), literal(program.addGift))[0];
      if (name && gift) {
        console.log(program.gifted);
        store.removeQuad(gift);
        gift = DataFactory.quad(
          name.subject,
          namedNode('http://hiea.de/contact#giftIdea'),
          literal("<s>" + program.addGift + "</s> (" + program.gifted + ")"),
          defaultGraph(),
        );
        store.addQuad(gift);
        console.log('„' + program.addGift + '“ marked as gifted with comment „' + program.gifted + '“.');
        saveContacts();
      } else {
        console.log('No gift „' + program.addGift + '“ exists for ' + program.name + '.');
      }
    }
  });
}



/* Removing attributes */

if (program.rmGift) {

  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      const name = store.getQuads(null, namedNode('http://hiea.de/contact#givenName'), literal(program.name))[0];
      const gift = store.getQuads(null, namedNode('http://hiea.de/contact#giftIdea'), literal(program.rmGift))[0];
      if (name && gift) {
        store.removeQuad(gift);
        console.log('„%s“ deleted as gift for ' + program.name + '.', program.rmGift);
        saveContacts();
      } else {
        console.log('No gift „' + program.rmGift + '“ exists for ' + program.name + '.');
      }
    }
  });
}

if (program.rmBirthday) {

  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      const name = store.getQuads(null, namedNode('http://hiea.de/contact#givenName'), literal(program.name))[0];
      const birthday = store.getQuads(null, namedNode('http://hiea.de/contact#birthday'), null)[0]; // only one birthday
      if (name && birthday) {
        store.removeQuad(birthday);
        console.log('Birthday deleted.');
        saveContacts();
      } else {
        console.log('No birthday exists for ' + program.name + '.');
      }
    }
  });
}

if (program.rmEmail) {

  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      const name = store.getQuads(null, namedNode('http://hiea.de/contact#givenName'), literal(program.name))[0];
      const removedEmail = store.getQuads(null, namedNode('http://hiea.de/contact#email'), literal(program.rmEmail))[0];
      if (name && removedEmail) {
        store.removeQuad(removedEmail);
        console.log('Email „%s“ deleted for ' + program.name + '.', program.rmEmail);
        saveContacts();
      } else {
        console.log('No email „' + program.rmEmail + '“ exists for ' + program.name + '.');
      }
    }
  });
}


if (program.rmPhone) {

  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      const name = store.getQuads(null, namedNode('http://hiea.de/contact#givenName'), literal(program.name))[0];
      const removedTel = store.getQuads(null, namedNode('http://hiea.de/contact#tel'), literal(program.rmPhone))[0];
      if (name && removedTel) {
        store.removeQuad(removedTel);
        console.log('Phone number „%s“ deleted for ' + program.name + '.', program.rmPhone);
        saveContacts();
      } else {
        console.log('No phone number „' + program.rmPhone + '“ exists for ' + program.name + '.');
      }
    }
  });
}


if (program.rmTag) {

  const parser = N3.Parser();
  const rdfStream = fs.createReadStream(_contactFile);
  parser.parse(rdfStream, (error, quad, prefixes) => {
    if (quad) {
      store.addQuad(quad);
    } else { // finished
      const removedTag = store.getQuads(null, namedNode('http://hiea.de/contact#tag'), literal(program.rmTag))[0];
      if (removedTag) {
        store.removeQuad(removedTag);
        console.log('„%s“ deleted.', program.rmTag);
        saveContacts();
      } else {
        console.log('No tag „' + program.rmTag + '“ exists for ' + program.name + '.');
      }
    }
  });
}



/* Save contacts */

function saveContacts() {
  fs.unlinkSync(_contactFile);
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


/* Print contacts */

function printContact(contact) {
  // name
  console.log(contact.object.value);

  // birthday
  store.forEach(function(birthday) {
    console.log("- birthday: " + birthday.object.value);
  }, contact.subject, namedNode('http://hiea.de/contact#birthday'), null);

  // emails
	i = 1;
  store.forEach(function(email) {
    console.log("- email " + i + ": " + email.object.value);
		i++;
  }, contact.subject, namedNode('http://hiea.de/contact#email'), null);

  // phone numbers
	i = 1;
  store.forEach(function(tel) {
    console.log("- tel " + i + ": " + tel.object.value);
		i++;
  }, contact.subject, namedNode('http://hiea.de/contact#tel'), null);

  // gifts
	i = 1;
  store.forEach(function(gift) {
    console.log("- gift " + i + ": " + gift.object.value);
		i++;
  }, contact.subject, namedNode('http://hiea.de/contact#giftIdea'), null);

  // tags
  var tagString = "";
  store.forEach(function(tag) {
    tagString += tag.object.value + ", ";
  }, contact.subject, namedNode('http://hiea.de/contact#tag'), null);
  if (tagString != "") {
    console.log("- tags: " + tagString.substring(0, tagString.length - 2));
  }
}

function printContacts() {
  store.forEach(function(contact) {
    printContact(contact);
    console.log('\r');
  }, null, namedNode('http://hiea.de/contact#givenName'), null);
}

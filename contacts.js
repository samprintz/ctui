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
  .parse(process.argv);

if (program.show) {
  console.log('Kontakte:');



}



if (program.add) {
  console.log('Füge hinzu: %s', program.add);

  const myQuad = quad(
    blankNode(),
    namedNode('http://xmlns.com/foaf/0.1/givenName'),
    literal(program.add),
    defaultGraph(),
  );

  store.addQuad(myQuad);

  const myQuad2 = quad(
    blankNode(),
    namedNode('http://xmlns.com/foaf/0.1/givenName'),
    literal("Peter"),
    defaultGraph(),
  );

  store.addQuad(myQuad2);

  saveContacts();

}

if (program.remove) {
  console.log('Lösche: %s', program.remove);
}


function saveContacts() {
  const writeStream = fs.createWriteStream('out.n3');
  const writer = N3.Writer(writeStream, { end: false, prefixes: { c: 'http://example.org/cartoons#' } });
  store.forEach(quad => writer.addQuad(quad));
  writer.end();
  console.log("Contacts saved");
}

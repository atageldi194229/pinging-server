const fs = require("fs");
const path = require("path");

const dir = path.join(__dirname, "data");

let regex = /[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json/gm;
let files = fs.readdirSync(dir).filter((e) => regex.test(e));

console.log(files);

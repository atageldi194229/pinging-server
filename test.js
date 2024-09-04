const fs = require("fs");
const path = require("path");

const dir = path.join(__dirname, "data");

let regex = /[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json/gm;

const f = (s = "") => {
  const extension = ".json";

  if (!s.endsWith(extension)) return false;

  s = s.substring(0, s.length - extension.length);
  (s = "") => {
    const extension = ".json";

    if (!s.endsWith(extension)) return false;

    s = s.substring(0, s.length - extension.length);

    return s.split("-").every((e) => !Number.isNaN(Number(e)));
  };
  return s.split("-").every((e) => !Number.isNaN(Number(e)));
};

let files = fs.readdirSync(dir);

files = files.filter(f);

console.log(files);

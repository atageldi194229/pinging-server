const fs = require("fs");
const axios = require("axios");
const path = require("path");

const today = new Date().toISOString().substring(0, 10);

const dir = path.join(__dirname, "data");
const file = path.join(__dirname, "data", "db.json");
const dateFile = path.join(__dirname, "data", today + ".json");
const fileListPath = path.join(__dirname, "data", "files.json");

const URL = process.env.URL;

if (!URL) {
  new Date().toISOString().substring(0, 10);
  console.log("URL is not defined");
  process.exit(1);
}

const getHost = (e) => `${e.ip}:${e.port}`;

const readFile = (filePath, defaultValue) => {
  if (fs.existsSync(filePath)) {
    return require(filePath);
  }

  return defaultValue;
};

const writeHostsToFiles = (data) => {
  let all = readFile(file, []);
  let newAdded = readFile(dateFile, []); // today added hosts

  let hosts = all.map(getHost);

  for (let e of data) {
    if (!hosts.includes(getHost(e))) {
      all.push(e);
      newAdded.push(e);
    }
  }

  fs.writeFileSync(file, JSON.stringify(all));

  all = fs.existsSync(dateFile) ? require(dateFile) : [];

  fs.writeFileSync(dateFile, JSON.stringify([...all, ...newAdded]));
};

axios.get(URL).then((res) => {
  if (res.status !== 200) return;

  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  writeHostsToFiles(res.data);
});

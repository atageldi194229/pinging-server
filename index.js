const fs = require("fs");
const axios = require("axios");
const path = require("path");

const today = new Date().toISOString().substring(0, 10);

const dir = path.join(__dirname, "data");
const hostListFile = path.join(__dirname, "data", "db.json");
const todayJsonFile = path.join(__dirname, "data", today + ".json");
const fileListPath = path.join(__dirname, "data", "files.json");

const getHost = (e) => `${e.ip}:${e.port}`;

const readFile = (file, defaultValue) => {
  return fs.existsSync(file) ? require(file) : defaultValue;
};

const writeHostsToFiles = (data) => {
  data = data.filter((e) => !getHost(e).includes("undefined"));
  let dbHosts = readFile(hostListFile, []);
  let newHosts = data.filter((e) => !dbHosts.includes(getHost(e)));

  let result = [...dbHosts, ...newHosts.map(getHost)];
  result = result.filter((e) => !e.includes("undefined"));

  fs.writeFileSync(hostListFile, JSON.stringify(result));

  // add new hosts to todays file
  let all = readFile(todayJsonFile, []);
  fs.writeFileSync(todayJsonFile, JSON.stringify([...all, ...newHosts]));

  let regex = /[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json/gm;
  let files = fs.readdirSync(dir).filter((e) => regex.test(e));
  fs.writeFileSync(fileListPath, JSON.stringify(files));
};

const fetchData = () => {
  const URL = process.env.URL;

  if (!URL) {
    new Date().toISOString().substring(0, 10);
    console.log("URL is not defined");
    process.exit(1);
  }

  axios.get(URL).then((res) => {
    if (res.status !== 200) return;

    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    writeHostsToFiles(res.data);
  });
};

fetchData();

const fs = require("fs");
const axios = require("axios");
const path = require("path");

const dir = path.join(__dirname, "data");
const file = path.join(__dirname, "data", "db.json");

const URL =
  process.env.URL ||
  "https://duralga-next-vercel.vercel.app/api/key_req?key=123&deviceId=qwerty";

if (!URL) {
  console.log("URL is not defined");
  process.exit(1);
}

const getHost = (e) => `${e.ip}:${e.port}`;

axios.get(URL).then((res) => {
  if (res.status !== 200) return;

  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  let db = [];
  let hosts = [];

  if (fs.existsSync(file)) {
    db = require(file);

    for (let e of db) {
      hosts.push(getHost(e));
    }
  }

  const { data } = res;

  for (let e of data) {
    if (!hosts.includes(getHost(e))) {
      db.push(e);
    }
  }

  fs.writeFileSync(file, JSON.stringify(db, null, 2));
});

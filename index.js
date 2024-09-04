const fs = require("fs");
const path = require("path");
const axios = require("axios");

const today = new Date().toISOString().substring(0, 10);

const dir = path.join(__dirname, "data");
const hostListFile = path.join(dir, "db.json");
const todayJsonFile = path.join(dir, today + ".json");
const fileListPath = path.join(dir, "files.json");

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

  let files = fs
    .readdirSync(dir)
    .filter((s = "") => {
      const extension = ".json";

      if (!s.endsWith(extension)) return false;

      s = s.substring(0, s.length - extension.length);

      return s.split("-").every((e) => !Number.isNaN(Number(e)));
    })
    .map((name) => {
      const filePath = path.join(dir, name);
      const sstpCount = require(filePath).length;
      const byteSize = fs.statSync(filePath).size;

      return {
        name,
        sstpCount,
        byteSize,
      };
    });

  fs.writeFileSync(fileListPath, JSON.stringify(files));
};

// const fetchData = () => {
//   const URL = process.env.URL;

//   console.log("URL:", URL);
  
//   if (!URL) {
//     console.error("URL is not defined");
//     process.exit(1);
//   }

//   return axios.get(URL).then((res) => {
//     if (res.status !== 200) return;

//     if (!fs.existsSync(dir)) {
//       fs.mkdirSync(dir, { recursive: true });
//     }

//     writeHostsToFiles(res.data);
//   });
// };

const fetchData2 = () => {
  const URL2 = process.env.URL2;

  console.log("URL2:", URL2);
  
  if (!URL2) {
    console.error("URL2 is not defined");
    process.exit(1);
  }

  return axios.get(URL2).then((res) => {
    if (res.status !== 200) return;

    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    writeHostsToFiles(res.data.data);
  });
};

// try {
//   console.log("started to fetch data...");
//   fetchData();
//   console.log("completed fetching data successfully");
// } catch (e) {
//   console.log("completed fetching data with error");
//   console.error(e);
// }

try {
  console.log("started to fetch data 2...");
  fetchData2();
  console.log("completed fetching data 2 successfully");
} catch (e) {
  console.log("completed fetching data 2 with error");
  console.error(e);
}

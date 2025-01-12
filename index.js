const axios = require('axios');
const fs = require('fs');
const path = require('path');


const url = process.env.URL2;


const today = new Date().toISOString().split('T')[0];


const dataDir = path.join(process.cwd(), "data");
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir);
}


const todayJsonFile = path.join(dataDir, `${today}.json`);
const dbFile = path.join(dataDir, "db.json");
const filesInfoFile = path.join(dataDir, "files.json");



const pattern = /(?:↑)?(?<id>\d+)•(?<sessions>\d+) SESSIONS.*?(?:USERS)?•(?<location_info>.*?)•(?<hostname>[A-Z0-9-]+\.OPENGW\.NET)(?::(?<port>[0-9]+))?•(?<country_info>.+?)•(?<ip>[0-9.]+)(?:↓)?|(?:↑)?(?<id_alt>\d+)•(?<sessions_alt>\d+) SESSIONS.*?•(?<location_info_alt>.*?)•(?<hostname_alt>[A-Z0-9-]+\.OPENGW\.NET)(?::(?<port_alt>[0-9]+))?•(?<country_info_alt>.+?)•(?<ip_alt>[0-9.]+)(?:↓)?/;

function parseLine(line) {
    const match = pattern.exec(line);
    if (match) {
        const { ip, port = 443, hostname, location_info, country_info, id, sessions } = match.groups;
        const locationParts = location_info ? location_info.split(" ") : match.groups.location_info_alt.split(" ");
        const countryParts = country_info ? country_info.split("~") : match.groups.country_info_alt.split("~");
        const shortCountry = countryParts[0].trim().split("-")[0];
        const countryName = countryParts[0].split("-")[1]?.trim() || "";
        const locationName = countryParts[1]?.trim() || "";

        return {
            hostname: hostname || match.groups.hostname_alt,
            ip: ip || match.groups.ip_alt,
            port: parseInt(port || match.groups.port_alt || 443, 10),
            info: `${sessions || match.groups.sessions_alt} SESSIONS ${locationParts.slice(1).join(" ")}`,
            info2: location_info || match.groups.location_info_alt,
            location: {
                country: countryName,
                short: shortCountry,
                name: locationName
            },
            id: id || match.groups.id_alt,
            key: `${ip || match.groups.ip_alt}:${port || match.groups.port_alt || 443}`
        };
    } else {
        console.debug(`Line did not match: ${line}`);
        return null;
    }
}


async function fetchData(url) {
    try {
        console.info(`Fetching data from URL: ${url}`);
        const response = await axios.get(url);
        console.debug(`Fetched data: ${response.data.slice(0, 500)}...`);
        return response.data.split('\n');
    } catch (error) {
        console.error(`Error fetching data: ${error.response?.status}`);
        return [];
    }
}


function saveDataToJson(data, filePath) {
    console.info(`Saving data to file: ${filePath}`);
    fs.writeFileSync(filePath, JSON.stringify(data, null, 0), 'utf-8');
}


function updateDb(ipPortList, dbFile) {
    let existingData = [];
    if (fs.existsSync(dbFile)) {
        existingData = JSON.parse(fs.readFileSync(dbFile, 'utf-8'));
    }

    const updatedData = Array.from(new Set([...existingData, ...ipPortList]));
    console.info(`Updated db.json with ${updatedData.length} unique entries (removed duplicates).`);
    fs.writeFileSync(dbFile, JSON.stringify(updatedData, null, 0), 'utf-8');
}


function updateFilesInfo(dataDir, filesInfoFile) {
    console.info(`Updating files info in ${filesInfoFile}`);
    const fileData = [];

    fs.readdirSync(dataDir).forEach(fileName => {
        if (fileName.endsWith(".json") && fileName !== "db.json" && fileName !== "files.json") {
            const filePath = path.join(dataDir, fileName);
            const fileContent = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
            const uniqueIps = new Set(fileContent.map(entry => entry.key)).size;
            const byteSize = fs.statSync(filePath).size;
            const creationTime = fs.statSync(filePath).ctimeMs;

            fileData.push({
                name: fileName,
                sstpCount: uniqueIps,
                byteSize,
                creationTime
            });
        }
    });


    fileData.sort((a, b) => a.creationTime - b.creationTime);
    fileData.forEach(entry => delete entry.creationTime);

    fs.writeFileSync(filesInfoFile, JSON.stringify(fileData, null, 0), 'utf-8');
    console.info(`files.json updated with ${fileData.length} entries.`);
}

(async function main() {
    const lines = await fetchData(url);
    const parsedData = lines
        .filter(line => line.includes("SESSIONS"))
        .map(line => parseLine(line))
        .filter(data => data !== null);


    saveDataToJson(parsedData, todayJsonFile);

    const ipPortList = parsedData.map(entry => entry.key);
    updateDb(ipPortList, dbFile);


    updateFilesInfo(dataDir, filesInfoFile);

    console.log(`today json file saved: ${todayJsonFile}`);
    console.log(`success, db updated`);
})();

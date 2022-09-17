const fs = require("fs");

const clean = (file) => {
  const data = require(file);

  fs.writeFileSync(
    file,
    JSON.stringify(data.filter((e) => e !== true && e !== false))
  );
};

clean("./data/2022-09-15.json");
clean("./data/2022-09-16.json");
clean("./data/2022-09-17.json");

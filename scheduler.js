const axios = require("axios");

const INTERVAL = 2 * 1000;
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_USERNAME = "atageldi194229";
const GITHUB_REPO = "pinging-server";
const WORKFLOW_ID = 34892269;

const run = () => {
  axios
    .post(
      `https://api.github.com/repos/${GITHUB_USERNAME}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_ID}/dispatches`,
      { ref: "main" },
      {
        headers: {
          Authorization: "Bearer: " + GITHUB_TOKEN,
        },
      }
    )
    .catch(console.error);
};

setInterval(run, INTERVAL);

run();

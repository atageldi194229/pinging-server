# Pinging Server

## Overview

The Pinging Server is a tool designed to monitor and track the response times of various network endpoints. It performs two main tasks:

1. **Ping Monitoring**: It continuously pings specified IP addresses or URLs to measure their round-trip time (RTT) in milliseconds. This helps in assessing the latency and availability of the network endpoints.

2. **Port Monitoring**: It checks the availability of a specific port (default is port 443) on the target IP addresses. This is useful for determining if services such as HTTPS are accessible.

## Features

- **Real-Time Monitoring**: Provides up-to-date RTT measurements for both ping and port checks.
- **Concurrent Processing**: Uses multithreading to perform multiple checks simultaneously, enhancing performance.
- **Logging**: Records results and errors in a log file for review and analysis.
- **Dynamic Configuration**: Configurable through environment variables, allowing for flexible usage in various environments.

## Usage

1. **Configuration**: Define the target IP addresses or URLs in the `target.txt` file. Each entry should be on a new line.

2. **Execution**: Run the script to start monitoring. The script will perform both ping and port checks and save the results to `output.txt`.

3. **Review Results**: Check `output.txt` for the results of the monitoring. The file will include RTT measurements for both ping and port checks.

## Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/haitovs/pinging-server-main.git
   ```

2. Install dependencies:

   ```sh
   npm install
   ```

3. Configure environment variables:

   - Set up `URL` and `URL2` in your environment or in a `.env` file, if required by the script.

4. Run the script:

   ```sh
   npm run build
   ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have improvements or fixes.

## License

This project is licensed under the MIT License.

---

Feel free to adjust any sections to better fit your project’s specifics!

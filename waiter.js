const seconds = Number(process.argv[2]);

setTimeout(() => {
  process.exit();
}, seconds * 1000);

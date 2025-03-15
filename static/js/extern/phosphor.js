// Local implementation of Phosphor Icons
// Original source: from https://unpkg.com/@phosphor-icons/web -> https://unpkg.com/@phosphor-icons/web@2.1.1/src/index.js

var head = document.getElementsByTagName("head")[0];

for (const weight of ["regular", "thin", "light", "bold", "fill", "duotone"]) {
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.type = "text/css";
    link.href = "/static/css/extern/phosphor/" + weight + "/style.css";
    head.appendChild(link);
}

// console.log("Phosphor Icons loaded (local implementation)");
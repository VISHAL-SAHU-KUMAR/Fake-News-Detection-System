const API = ["localhost", "127.0.0.1"].includes(window.location.hostname)
    ? "http://localhost:8001"
    : "/api";
let token = localStorage.getItem("tl_token");
let user = null;
let pendingEmail = "";

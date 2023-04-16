import axios, { AxiosInstance } from "axios";

const instance: AxiosInstance = axios.create({
  baseURL: "http://localhost:5001",
  timeout: 60000, // gpt requests can take a long time :)
  headers: {
    "Content-Type": "application/json",
  },
});

export default instance;

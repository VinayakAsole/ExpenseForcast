// Firebase configuration
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyAwsJ30SnKHIZLJ6rqHKfGadY_QHvlISyo",
  authDomain: "phisher-f3680.firebaseapp.com",
  databaseURL: "https://phisher-f3680-default-rtdb.firebaseio.com",
  projectId: "phisher-f3680",
  storageBucket: "phisher-f3680.firebasestorage.app",
  messagingSenderId: "825293777225",
  appId: "1:825293777225:web:788d4987e79f4bfe8cd298",
  measurementId: "G-6VRX7BXP3E"
};

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };

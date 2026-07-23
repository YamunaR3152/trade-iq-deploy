// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";
import { getAuth } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBOOJfdXxrbgR6lmGHjrFPlGwx24-NCtyw",
  authDomain: "tradeiq-26.firebaseapp.com",
  projectId: "tradeiq-26",
  storageBucket: "tradeiq-26.firebasestorage.app",
  messagingSenderId: "1013397127798",
  appId: "1:1013397127798:web:291855f83ec0abf0659557",
  measurementId: "G-WQZ7BE0H9Q"
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);
export const firebaseAuth = getAuth(app);

export const analyticsPromise =
  typeof window !== "undefined" ? isSupported().then((supported) => (supported ? getAnalytics(app) : null)) : Promise.resolve(null);

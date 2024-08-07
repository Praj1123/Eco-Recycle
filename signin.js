import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-app.js";
import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-auth.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDQuXXlYBuj-QES1D8GonoW8W9fXB2GJiI",
  authDomain: "recyclotech-79fb4.firebaseapp.com",
  projectId: "recyclotech-79fb4",
  storageBucket: "recyclotech-79fb4.appspot.com",
  messagingSenderId: "751759542870",
  appId: "1:751759542870:web:4d83de4c24bba603c549f7"
};

const app = initializeApp(firebaseConfig);
const submit = document.getElementById('submit');

submit.addEventListener('click',function(event){
    event.preventDefault()
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const auth = getAuth();
    signInWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
        // Signed up 
        const user = userCredential.user;
        alert("Logged in Successfully");
        window.location.href = "profile.html";
        // ...
    })
    .catch((error) => {
        const errorCode = error.code;
        const errorMessage = error.message;
        console.log(error);
        // ..
    });
});
async function generateVideo() {
  const prompt = document.getElementById("prompt").value.trim();
  const duration = document.getElementById("duration").value;
const style = document.getElementById("style").value;
  const status = document.getElementById("status");
  const result = document.getElementById("result");

  if (!prompt) {
    status.textContent = "⚠️ Pehle video idea likho.";
    return;
  }

  status.textContent = "⏳ AI video generate ho rahi hai... Please wait.";

  result.innerHTML = `
    <h2>🎬 Generating Video...</h2>
    <p>AI aapki video bana raha hai. Is mein kuch waqt lag sakta hai.</p>
  `;

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
  prompt: prompt,
  duration: duration,
  style: style
})
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.error || "Video generation failed.");
    }

    status.textContent = "✅ Video ready!";

    result.innerHTML = `
      <h2>🎬 Your Video</h2>
      <video controls width="100%">
        <source src="${data.video}" type="video/mp4">
        Your browser does not support video playback.
      </video>
      <br><br>
      <a href="${data.video}" download class="download-btn">
        📥 Download Video
      </a>
    `;

  } catch (error) {
    console.error(error);

    status.textContent = "❌ Video generate nahi ho saki.";

    result.innerHTML = `
      <h2>❌ Error</h2>
      <p>${error.message}</p>
    `;
  }
}


// SIGN UP
async function signupUser() {
  const nameInput = document.querySelector(
    '#signupPopup input[placeholder="Full name"]'
  );

  const emailInput = document.querySelector(
    '#signupPopup input[placeholder="Email address"]'
  );

  const passwordInput = document.querySelector(
    '#signupPopup input[placeholder="Create password"]'
  );

  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (!name || !email || !password) {
    alert("Please fill all fields.");
    return;
  }

  try {
    const response = await fetch("/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: name,
        email: email,
        password: password
      })
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.error || "Sign up failed.");
    }

    alert("✅ Account created successfully!");

    closeAuth();

    updateUserUI(data.name);

  } catch (error) {
    alert("❌ " + error.message);
  }
}


// LOGIN
async function loginUser() {
  const emailInput = document.querySelector(
    '#loginPopup input[placeholder="Email address"]'
  );

  const passwordInput = document.querySelector(
    '#loginPopup input[placeholder="Password"]'
  );

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (!email || !password) {
    alert("Please enter email and password.");
    return;
  }

  try {
    const response = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email: email,
        password: password
      })
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.error || "Login failed.");
    }

    alert("✅ Login successful!");

    closeAuth();

    updateUserUI(data.name);

  } catch (error) {
    alert("❌ " + error.message);
  }
}


// LOGOUT
async function logoutUser() {
  try {
    await fetch("/logout", {
      method: "POST"
    });

    location.reload();

  } catch (error) {
    console.error(error);
  }
}


// USER UI
function updateUserUI(name) {
  const authButtons = document.querySelector(".auth-buttons");

  if (!authButtons) {
    return;
  }

  authButtons.innerHTML = `
    <span class="welcome-user">👤 ${name}</span>
    <button class="signup-btn" onclick="logoutUser()">Logout</button>
  `;
}


// CHECK LOGIN
async function checkLogin() {
  try {
    const response = await fetch("/me");
    const data = await response.json();

    if (data.logged_in) {
      updateUserUI(data.name);
    }

  } catch (error) {
    console.error("Login check failed:", error);
  }
}


// Check login when page opens
checkLogin();
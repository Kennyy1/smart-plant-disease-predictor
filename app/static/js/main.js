document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("leafImage");
    const previewImage = document.getElementById("imagePreview");
    const previewPlaceholder = document.getElementById("previewPlaceholder");
    const loadingBox = document.getElementById("loadingBox");
    const predictionForm = document.getElementById("predictionForm");
    const signupForm = document.getElementById("signupForm");
    const signupPassword = document.getElementById("signupPassword");
    const signupConfirmPassword = document.getElementById("signupConfirmPassword");
    const passwordMatchText = document.getElementById("passwordMatchText");
    const passwordStrengthText = document.getElementById("passwordStrengthText");
    const passwordStrengthBar = document.getElementById("passwordStrengthBar");
    const signupSubmitButton = document.getElementById("signupSubmitButton");
    const signupLoadingSpinner = document.getElementById("signupLoadingSpinner");
    const signupFeedback = document.getElementById("signupFeedback");
    const passwordToggles = document.querySelectorAll("[data-password-toggle]");

    const getPasswordStrength = (password) => {
        let score = 0;

        if (password.length >= 6) score += 1;
        if (password.length >= 10) score += 1;
        if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score += 1;
        if (/\d/.test(password)) score += 1;
        if (/[^A-Za-z0-9]/.test(password)) score += 1;

        if (score <= 2) return { label: "Weak", className: "strength-weak" };
        if (score <= 4) return { label: "Medium", className: "strength-medium" };
        return { label: "Strong", className: "strength-strong" };
    };

    const updateSignupState = () => {
        if (
            !signupPassword ||
            !signupConfirmPassword ||
            !passwordMatchText ||
            !passwordStrengthText ||
            !passwordStrengthBar ||
            !signupSubmitButton ||
            !signupFeedback
        ) {
            return;
        }

        const password = signupPassword.value;
        const confirmPassword = signupConfirmPassword.value;
        const passwordBytes = new TextEncoder().encode(password).length;
        const isLengthValid = password.length >= 6 && passwordBytes <= 72;
        const isMatch = password.length > 0 && password === confirmPassword;
        const strength = getPasswordStrength(password);

        passwordStrengthText.textContent = `Strength: ${strength.label}`;
        passwordStrengthBar.className = `strength-meter-bar ${strength.className}`;

        if (!password.length && !confirmPassword.length) {
            passwordMatchText.textContent = "Passwords do not match";
            passwordMatchText.className = "password-match-text text-muted mb-0";
            signupFeedback.textContent =
                "Passwords must be 6 to 72 characters, and the confirmation must match before you can sign up.";
            signupFeedback.className = "signup-feedback-panel";
        } else if (!isLengthValid) {
            passwordMatchText.textContent = "Password length is invalid";
            passwordMatchText.className = "password-match-text text-danger mb-0";
            signupFeedback.textContent = "Use a password between 6 and 72 characters.";
            signupFeedback.className = "signup-feedback-panel signup-feedback-error";
        } else if (isMatch) {
            passwordMatchText.textContent = "Passwords match";
            passwordMatchText.className = "password-match-text text-success mb-0";
            signupFeedback.textContent = "Your password looks good and matches the confirmation.";
            signupFeedback.className = "signup-feedback-panel signup-feedback-success";
        } else {
            passwordMatchText.textContent = "Passwords do not match";
            passwordMatchText.className = "password-match-text text-danger mb-0";
            signupFeedback.textContent = "Please make sure both password fields match exactly.";
            signupFeedback.className = "signup-feedback-panel signup-feedback-error";
        }

        signupSubmitButton.disabled = !(isLengthValid && isMatch);
    };

    if (fileInput && previewImage && previewPlaceholder) {
        fileInput.addEventListener("change", (event) => {
            const [file] = event.target.files;
            if (!file) {
                previewImage.classList.add("d-none");
                previewImage.src = "";
                previewPlaceholder.classList.remove("d-none");
                return;
            }

            const imageUrl = URL.createObjectURL(file);
            previewImage.src = imageUrl;
            previewImage.classList.remove("d-none");
            previewPlaceholder.classList.add("d-none");
        });
    }

    if (predictionForm && loadingBox) {
        predictionForm.addEventListener("submit", () => {
            loadingBox.classList.remove("d-none");
        });
    }

    if (signupForm && signupPassword && signupConfirmPassword) {
        updateSignupState();

        signupPassword.addEventListener("input", updateSignupState);
        signupConfirmPassword.addEventListener("input", updateSignupState);

        signupForm.addEventListener("submit", (event) => {
            updateSignupState();
            if (signupSubmitButton && signupSubmitButton.disabled) {
                event.preventDefault();
                return;
            }

            if (signupLoadingSpinner && signupSubmitButton) {
                signupLoadingSpinner.classList.remove("d-none");
                signupSubmitButton.disabled = true;
            }
        });
    }

    if (passwordToggles.length) {
        passwordToggles.forEach((toggle) => {
            toggle.addEventListener("click", () => {
                const targetId = toggle.getAttribute("data-password-toggle");
                const input = targetId ? document.getElementById(targetId) : null;
                if (!input) {
                    return;
                }

                const isPassword = input.type === "password";
                input.type = isPassword ? "text" : "password";
                toggle.textContent = isPassword ? "Hide" : "Show";
                toggle.setAttribute("aria-label", isPassword ? "Hide password" : "Show password");
            });
        });
    }
});

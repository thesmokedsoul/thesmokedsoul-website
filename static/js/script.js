document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#booking-form");
  const steps = document.querySelectorAll(".form-step");
  const nextButtons = document.querySelectorAll(".next");
  const backButtons = document.querySelectorAll(".back");

  let currentStep = 0;

  function showStep(index) {
    steps.forEach((step, i) => {
      step.classList.toggle("active", i === index);
      step.style.display = i === index ? "block" : "none";
    });
  }

  function validateCurrentStep() {
    const currentFields = steps[currentStep].querySelectorAll("input, textarea, select");

    for (const field of currentFields) {
      if (!field.checkValidity()) {
        field.reportValidity();
        return false;
      }
    }

    return true;
  }

  if (steps.length > 0) {
    showStep(currentStep);
  }

  nextButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();

      if (!validateCurrentStep()) {
        return;
      }

      if (currentStep < steps.length - 1) {
        currentStep++;
        showStep(currentStep);
      }
    });
  });

  backButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();

      if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
      }
    });
  });

  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      if (!validateCurrentStep()) {
        return;
      }

      const formData = new FormData(form);

      try {
        const response = await fetch("/submit-booking", {
          method: "POST",
          body: formData
        });

        const data = await response.json();

        alert(data.message || "You are on the board. We will be in touch shortly.");

        if (data.redirect) {
          window.location.href = data.redirect;
        }
      } catch (error) {
        console.error("Booking form error:", error);
        alert("Something went wrong. Please try again or reach out directly.");
      }
    });
  }
});
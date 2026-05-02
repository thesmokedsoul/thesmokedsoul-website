document.addEventListener("DOMContentLoaded", () => {
  const steps = document.querySelectorAll(".form-step");
  const nextButtons = document.querySelectorAll("[data-next]");
  const prevButtons = document.querySelectorAll("[data-prev]");

  let currentStep = 0;

  function showStep(index) {
    steps.forEach((step, i) => {
      step.style.display = i === index ? "block" : "none";
    });
  }

  if (steps.length > 0) {
    showStep(currentStep);
  }

  nextButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();

      if (currentStep < steps.length - 1) {
        currentStep++;
        showStep(currentStep);
      }
    });
  });

  prevButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();

      if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
      }
    });
  });
});
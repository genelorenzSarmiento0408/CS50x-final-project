const school_role = document.getElementById("school_role");
const grade = document.getElementById("grade");
const section = document.getElementById("section");

if (window.location.pathname === "/register") {
  school_role.addEventListener("change", () => {
    if (school_role.value === "Teacher" || school_role.value === "Principal") {
      grade.removeAttribute("required");
      section.removeAttribute("required");
      grade.style.display = "none";
      section.style.display = "none";
    } else {
      grade.style.display = "block";
      section.style.display = "block";
    }
  });
}

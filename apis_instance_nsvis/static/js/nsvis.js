function overlay(element) {
  let x = element.dataset.x;
  let y = element.dataset.y;
  let height = element.dataset.height;
  let width = element.dataset.width;
  let target = element.dataset.target;
  let image = document.getElementById(target);
  let rect = image.getBoundingClientRect();
  element.style.position = "absolute";
  element.style.left = rect.left+(x/100*rect.width)-5+"px";
  element.style.top = rect.top+(y/100*rect.height)-5+"px";
  element.style.width = width/100*rect.width+10+"px";
  element.style.height = height/100*rect.height+10+"px";
  element.style.background = "red";
}
function overlay_all() {
  document.querySelectorAll(".overlay").forEach(element => {
    overlay(element);
  });
}
window.addEventListener("resize", function(event) {
  overlay_all();
});
document.addEventListener('readystatechange', (event) => {
  if (event.target.readyState === "complete") {
    overlay_all();
  }
});

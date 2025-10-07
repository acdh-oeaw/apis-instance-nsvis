function Rect(x, y, width, height, annotationId = null) {
  this.annotationId = annotationId;
  this.x = x;
  this.y = y;
  this.width = width;
  this.height = height;
  this.selected = false;
  this.area = function() {
    return (Math.abs(this.width) * Math.abs(this.height));
  };
  this.contains = function(x, y, padding = 10) {
    rx = this.x + padding;
    rwidth = this.width - padding + rx;
    ry = this.y + padding;
    rheight = this.height - padding + ry;
    if ((rx < x) && (x < rwidth) && (ry < y) && (y < rheight)) {
      return true;
    }
    return false;
  };
  this.toggle = function() {
    this.selected = !this.selected;
  };
  this.unselect = function() {
    this.selected = false;
  };
}

function redrawrects(ctx, rects) {
  ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas
  for (var i = 0; i < rects.length; i++) {
    rect = rects[i];
    ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
    if (rect.selected) {
      ctx.fillStyle = "rgba(255, 0, 0, 0.5)";
    }
    ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
  }
  ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
}

function rectPercentage(ctx, rect) {
  let canvasRect = canvas.getBoundingClientRect();
  let x = rect.x / canvasRect.width * 100;
  let y = rect.y / canvasRect.height * 100;
  let height = rect.height / canvasRect.height * 100;
  let width = rect.width / canvasRect.width * 100;
  return [x, y, height, width];
}


const canvas = document.getElementById('canvas');
let rect = canvas.getBoundingClientRect();
const ctx = canvas.getContext('2d');
let rects = [];
document.querySelectorAll(".overlay").forEach(element => {
  let annotationId = element.dataset.annotationId;
  let x = element.dataset.x / 100 * rect.width;
  let y = element.dataset.y / 100 * rect.height;
  let width = element.dataset.width / 100 * rect.width;
  let height = element.dataset.height / 100 * rect.height;
  r = new Rect(x, y, width, height, annotationId);
  rects.push(r);
});
redrawrects(ctx, rects);


let isDrawing = false;
let startX, startY, width, height;

canvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    startX = e.offsetX;
    startY = e.offsetY;
    width = 0;
    height = 0;
});

canvas.addEventListener('mousemove', (e) => {
    if (!isDrawing) return;
    redrawrects(ctx, rects);
    width = e.offsetX - startX;
    height = e.offsetY - startY;
    ctx.fillRect(startX, startY, width, height);
});

canvas.addEventListener('mouseup', () => {
    r = new Rect(startX, startY, width, height);
    if (r.area() > 1000) {
    	console.log("Adding new rect: " + r.area());
	rects.push(r);
    }
    isDrawing = false;
    redrawrects(ctx, rects);
});

canvas.addEventListener("click", (e) => {
  x = e.offsetX;
  y = e.offsetY;
  for (var i = 0; i < rects.length; i++) {
    rects[i].contains(x, y) ? rects[i].toggle() : rects[i].unselect();
    rects[i].selected && openAnnotationForm(rects[i]);
  }
  redrawrects(ctx, rects);
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Delete") {
    rects = rects.filter(function(x) { return !x.selected });
    redrawrects(ctx, rects);
  }
});

function openAnnotationForm(rect) {
  form = document.getElementById("form-template").cloneNode(true);
  form.classList.remove("d-none");
  formcontainer = document.getElementById("form");
  if (rect.annotationId) {
  } else {
    [x, y, height, width] = rectPercentage(rect, ctx);
    formcontainer.appendChild(form);
    console.log(formcontainer);
  }
}

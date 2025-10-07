function Rect(x, y, width, height, prefix = null) {
    this.prefix = prefix;
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
    this.select = function() {
        this.selected = true;
    };
}

function redrawrects(ctx, rects) {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas
    document.querySelectorAll("details").forEach(details => {
        details.style.display = "none";
    });
    for (var i = 0; i < rects.length; i++) {
        rect = rects[i];
        ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
        if (rect.selected) {
            ctx.fillStyle = "rgba(255, 0, 0, 0.5)";
        }
        ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
        document.getElementById("details-" + rect.prefix).style.display = "block";
    }
    newform = document.getElementById("details-form-" + getNewFormIndex());
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

document.querySelectorAll(".input-data").forEach(dataInput => {
    if (JSON.parse(dataInput.value)) {
        data = JSON.parse(dataInput.value);
        let prefix = dataInput.name.replace("-data", "");
        let x = data.x / 100 * rect.width;
        let y = data.y / 100 * rect.height;
        let width = data.width / 100 * rect.width;
        let height = data.height / 100 * rect.height;
        r = new Rect(x, y, width, height, prefix);
        rects.push(r);
    }
});

document.querySelectorAll("details").forEach(details => {
    console.log(details);
    details.addEventListener("click", function() {
        console.log("toggle");
        prefix = details.id.replace("details-", "");
        console.log(prefix);
        for (var i = 0; i < rects.length; i++) {
            if (details.open) {
                rects[i].prefix == prefix && rects[i].unselect();
            } else {
                rects[i].prefix == prefix && rects[i].select();
            }
        }
        redrawrects(ctx, rects);
    });
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
    //rects = rects.filter(function(x) { return x.prefix });
    redrawrects(ctx, rects);
    width = e.offsetX - startX;
    height = e.offsetY - startY;
    ctx.fillRect(startX, startY, width, height);
});

canvas.addEventListener('mouseup', () => {
    prefix = "form-" + getNewFormIndex();
    r = new Rect(startX, startY, width, height, prefix);
    if (r.area() > 1000) {
        console.log("Adding new rect: " + r.area());
        rects.push(r);
        last_form_id = getNewFormIndex();
        [x, y, height, width] = rectPercentage(ctx, r);
        data = {
            "x": x,
            "y": y,
            "height": height,
            "width": width
        };
        document.querySelector("#id_form-" + last_form_id + "-data").value = JSON.stringify(data);
    }
    isDrawing = false;
    redrawrects(ctx, rects);
});

canvas.addEventListener("click", (e) => {
    x = e.offsetX;
    y = e.offsetY;
    document.querySelectorAll("details").forEach(dialog => {
        dialog.removeAttribute("open");
    });
    for (var i = 0; i < rects.length; i++) {
        rects[i].contains(x, y) ? rects[i].toggle() : rects[i].unselect();
        rects[i].selected && document.getElementById("details-" + rects[i].prefix).setAttribute("open", "");
    }
    redrawrects(ctx, rects);
});

function getNewFormIndex() {
    total_forms = document.getElementById("id_form-TOTAL_FORMS").value;
    return parseInt(total_forms) - 1;
}

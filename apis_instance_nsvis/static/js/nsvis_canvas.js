const defaultFillStyle = "rgba(255, 255, 255, 0.5)";
/*
 * Container for storing one rectangle
 * We store the x, y, width, height values in absolute numbers,
 * because that is what is used for drawing the rectangle in the canvas.
 * But we have the `percentage` method that calculates the position
 * in the canvas in relative numbers and that is whats saved.
 */
function Rect(x, y, width, height, id, color = "rgba(255, 255, 255, 0.5)") {
    this.id = id;
    this.color = color;
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
    this.percentage = function(canvas) {
        let canvasRect = canvas.getBoundingClientRect();
        let x = this.x / canvasRect.width * 100;
        let y = this.y / canvasRect.height * 100;
        let height = this.height / canvasRect.height * 100;
        let width = this.width / canvasRect.width * 100;
        return {
            "x": x,
            "y": y,
            "height": height,
            "width": width
        };
    };
}

/*
 * The list of rects that are currently present in the DOM
 */
let rects = [];

/*
 * Write some text in the top middle of the rect
 */
function drawRectTitle(ctx, rect, text) {
    text = text.replace(/(\r\n|\r|\n)/gm, "");
    text = text.replace(/ +/g, ' ');
    text = text.trim();
    fontsize = Math.min(rect.height / 10, 20);
    ctx.font = `${fontsize}px Arial`;
    textwidth = ctx.measureText(text).width;
    while (textwidth > rect.width) {
        text = text.slice(0, text.length - 6);
        textwidth = ctx.measureText(text).width;
        text = `${text}...`;
    }
    textwidth = ctx.measureText(text).width;
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    ctx.fillStyle = "rgba(255, 255, 255)";
    ctx.fillRect(rect.x + rect.width / 2 - textwidth / 2 - 5, rect.y + 5, textwidth + 10, fontsize + 10);
    ctx.fillStyle = "rgba(0, 0, 0)";
    ctx.fillText(text, rect.x + rect.width / 2, rect.y + 10)
}

/*
 * Redraw all the rects in the canvas
 */
function redrawrects(ctx, rects) {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas
    for (var i = 0; i < rects.length; i++) {
        rect = rects[i];
        ctx.fillStyle = rect.color;
        if (rect.selected) {
            ctx.fillStyle = "rgba(255, 0, 0, 0.5)";
        }
        ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
        text = document.getElementById(`details-form-${rect.id}`).querySelector("summary").textContent;
        drawRectTitle(ctx, rect, text);
    }
    // Reset the fillStyle to the default
    ctx.fillStyle = defaultFillStyle;
}

/*
 * Initialize the Canvas used for displaying the image and drawing
 */

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

/*
 * Go through all the inputs that have the `.input-data` class
 * and use their values to generate the initial list of rectangles
 */
document.querySelectorAll(".input-data").forEach(dataInput => {
    if (JSON.parse(dataInput.value)) {
        data = JSON.parse(dataInput.value);
        let rect = canvas.getBoundingClientRect();
        let id = dataInput.name.replace(/[^0-9]/g, "");
        let x = data.x / 100 * rect.width;
        let y = data.y / 100 * rect.height;
        let width = data.width / 100 * rect.width;
        let height = data.height / 100 * rect.height;
        r = new Rect(x, y, width, height, id);
        rects.push(r);
    }
});

// Draw initial rectangles
redrawrects(ctx, rects);

/*
 * Mark a Rectangle as selected based on the corresponding `details` element
 */
function detailsToggleEventListener(details) {
    id = details.id.replace(/[^0-9]/g, "");
    for (var i = 0; i < rects.length; i++) {
        if (details.open) {
            rects[i].id == id && rects[i].unselect();
        } else {
            rects[i].id == id && rects[i].select();
        }
    }
    redrawrects(ctx, rects);
}

document.querySelectorAll("details").forEach(details => {
    details.addEventListener("click", function() {
        detailsToggleEventListener(details)
    });
});

/*
 * If we receive a "Delete" key and one of the rectanges is currently selected and
 * that rectangle is a new one (its ID is greater than the number of initial forms)
 * remove that rectangle from the list of rectanges and redraw the rectangles.
 */
document.addEventListener("keydown", (e) => {
    if (e.key == "Delete") {
        initialForms = document.getElementById("id_form-INITIAL_FORMS").value;
        for (var i = 0; i < rects.length; i++) {
            rect = rects[i];
            if (rect.selected) {
                if (rect.id >= initialForms) {
                    detailsElement = document.getElementById(`details-form-${rect.id}`);
                    detailsElement.remove();
                    rects.splice(i, 1);
                    document.getElementById("id_form-TOTAL_FORMS").value--;
                }
            }
        }
        redrawrects(ctx, rects);
    }
});


/*
 * Draw on the canvas
 */

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

/* If the rectangle is greater than a specific size,
 * add it to the list of recangles and create a form
 * for the rectangle.
 */
canvas.addEventListener('mouseup', () => {
    r = new Rect(startX, startY, width, height);
    if (r.area() > 1000) {
        formCount = document.getElementById("id_form-TOTAL_FORMS").value;
        r.id = formCount;
        r.color = "rgba(255, 127, 0, 0.5)";
        console.log("Adding new rect: " + r.area());
        rects.push(r);
        emptyForm = document.querySelector('#details-form-__prefix__').cloneNode(true);
        emptyForm.id = emptyForm.id.replace(/__prefix__/g, formCount);
        emptyForm.innerHTML = emptyForm.innerHTML.replace(/__prefix__/g, formCount);
        emptyForm.addEventListener("click", function() {
            detailsToggleEventListener(emptyForm)
        });
        emptyForm.querySelector("#id_form-" + formCount + "-data").value = JSON.stringify(r.percentage(canvas));
        submitButton = document.getElementById("submit");
        submitButton.before(emptyForm);
        document.getElementById("id_form-TOTAL_FORMS").value++;

    }
    isDrawing = false;
    redrawrects(ctx, rects);
});

/*
 * Select or deselect a rectangle on click in the canvas
 */
canvas.addEventListener("click", (e) => {
    x = e.offsetX;
    y = e.offsetY;
    document.querySelectorAll("details").forEach(dialog => {
        dialog.removeAttribute("open");
    });
    for (var i = 0; i < rects.length; i++) {
        rects[i].contains(x, y) ? rects[i].toggle() : rects[i].unselect();
        rects[i].selected && document.getElementById(`details-form-${rects[i].id}`).setAttribute("open", "");
    }
    redrawrects(ctx, rects);
});

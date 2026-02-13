# Icon Replacement Template & Guide

## Quick Copy-Paste CSS Template

Use this pattern for **every icon replacement**. Just change the class names and sizes.

```css
/* Hide old Font Awesome <i> tag */
.your-class-name i {
    display: none;
}

/* Style the new SVG <img> */
.your-class-name img {
    width: 18px;
    height: 18px;
    vertical-align: middle;
    object-fit: contain;
}
```

---

## Step-by-Step: How to Replace ANY Icon

### Step 1: Find the Icon's Class Name
```html
<!-- Example: Old Font Awesome icon -->
<div class="my-icon-class">
    <i class="fas fa-phone"></i>
    Contact
</div>
```
**Class name:** `.my-icon-class`

### Step 2: Add CSS to Hide the Old Icon
In `static/css/style.css`, add:
```css
.my-icon-class i {
    display: none;
}
```

### Step 3: Add CSS to Style the New SVG
```css
.my-icon-class img {
    width: 18px;
    height: 18px;
    vertical-align: middle;
    margin-right: 5px;  /* Optional: space between icon and text */
}
```

### Step 4: Update the HTML
Replace the `<i>` tag with:
```html
<div class="my-icon-class">
    <img src="/static/uploads/phone.svg" alt="phone">
    Contact
</div>
```

### Step 5: Add Color to the SVG File
Open `static/uploads/phone.svg` and change:
```xml
stroke="currentColor"  →  stroke="#334155"
```

---

## Real Examples (Copy & Customize)

### Example 1: Location Icon (Already Done)
**CSS in `style.css`:**
```css
.property-location i {
    display: none;
}

.property-location img {
    width: 18px;
    height: 18px;
    vertical-align: middle;
}
```

**HTML in template:**
```html
<p class="property-location">
    <img src="/static/uploads/map-pin.svg" alt="location">
    {{ property.location }}
</p>
```

---

### Example 2: Phone Icon
**CSS in `style.css`:**
```css
.phone-icon i {
    display: none;
}

.phone-icon img {
    width: 16px;
    height: 16px;
    vertical-align: middle;
    margin-right: 8px;
}
```

**HTML in template:**
```html
<a href="tel:+254784666927" class="phone-icon">
    <img src="/static/uploads/phone.svg" alt="phone">
    0784 666 927
</a>
```

---

### Example 3: Email Icon
**CSS in `style.css`:**
```css
.email-icon i {
    display: none;
}

.email-icon img {
    width: 16px;
    height: 16px;
    vertical-align: middle;
    margin-right: 8px;
}
```

**HTML in template:**
```html
<a href="mailto:info@landvista.com" class="email-icon">
    <img src="/static/uploads/envelope.svg" alt="email">
    Email Us
</a>
```

---

### Example 4: WhatsApp Icon
**CSS in `style.css`:**
```css
.whatsapp-icon i {
    display: none;
}

.whatsapp-icon img {
    width: 18px;
    height: 18px;
    vertical-align: middle;
    margin-right: 8px;
}
```

**HTML in template:**
```html
<a href="https://wa.me/254784666927" class="whatsapp-icon">
    <img src="/static/uploads/whatsapp.svg" alt="whatsapp">
    WhatsApp
</a>
```

---

### Example 5: Search Icon
**CSS in `style.css`:**
```css
.search-icon i {
    display: none;
}

.search-icon img {
    width: 20px;
    height: 20px;
    vertical-align: middle;
}
```

**HTML in template:**
```html
<button class="search-icon">
    <img src="/static/uploads/search.svg" alt="search">
</button>
```

---

## Troubleshooting

### Icon Still Showing (Red or Old Icon Visible)
1. Check if there's a **::before** or **::after** in the CSS
2. Make sure you added `display: none;` to `.your-class i`
3. Hard refresh: **Ctrl+F5** (Windows) or **Cmd+Shift+R** (Mac)

### Icon Looks Blurry or Wrong Size
- Adjust `width` and `height` in the CSS
- Add `object-fit: contain;` to prevent stretching
- Add `filter: grayscale(0.3);` if you need to adjust the appearance

### SVG Has No Color
Open the SVG file and change:
```xml
stroke="currentColor"  →  stroke="#334155"
fill="none"            →  fill="none"     (keep this)
```

---

## SVG Color Reference

| Color | Hex Code | Use Case |
|-------|----------|----------|
| Dark Gray | `#334155` | Professional, default |
| Black | `#000000` | Bold, high contrast |
| Dark Blue | `#1e40af` | Professional, corporate |
| Green | `#16a34a` | Success, positive |
| Red | `#dc2626` | Alert, important |
| Orange | `#ea580c` | Warning, attention |

---

## File Naming Convention

When downloading SVGs, save them with these names:

```
phone.svg           → Phone icon
envelope.svg        → Email icon
map-pin.svg         → Location icon
search.svg          → Search icon
menu.svg            → Menu/hamburger icon
close.svg           → Close/X icon
check.svg           → Checkmark icon
arrow-right.svg     → Right arrow icon
star.svg            → Star/rating icon
```

---

## Quick Checklist for Each Icon

- [ ] Download SVG from Tabler Icons, Feather Icons, or Heroicons
- [ ] Save to `static/uploads/[icon-name].svg`
- [ ] Open SVG file and add color: `stroke="#334155"`
- [ ] Find the HTML with the old `<i>` tag
- [ ] Replace `<i>` with `<img src="/static/uploads/[icon-name].svg" alt="[description]">`
- [ ] Add CSS to hide old icon: `.class-name i { display: none; }`
- [ ] Add CSS to style new image: `.class-name img { width: 18px; height: 18px; }`
- [ ] Hard refresh browser (Ctrl+F5)
- [ ] Test and verify icon appears


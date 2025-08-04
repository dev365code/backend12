<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<link rel="stylesheet" href="<c:url value='/publish/rolling.css'/>">

<div class="carousel">
  <div class="slides">
    <img src="/image/image0.png" class="slide active">
    <img src="/image/image1.png" class="slide">
    <img src="/image/image2.png" class="slide">
    <img src="/image/image3.png" class="slide">
    <img src="/image/image4.png" class="slide">
    <img src="/image/image5.png" class="slide">
    <img src="/image/image6.png" class="slide">
  </div>
  <button class="prev">&#10094;</button>
  <button class="next">&#10095;</button>
</div>

<style>
  .carousel {
    position: relative;
    z-index: 1;
  }

.slides {
  display: flex;
  transition: transform 0.5s ease-in-out;
}

.slide {
  min-width: 100%;
  display: none;
}

.slide.active {
  display: block;
}

button.prev, button.next {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  font-size: 30px;
  background: rgba(0,0,0,0.3);
  color: white;
  border: none;
  cursor: pointer;
  padding: 10px;
  z-index: 1;
}

button.prev {
  left: 10px;
}
button.next {
  right: 10px;
}
</style>

<script>
let current = 0;
const slides = document.querySelectorAll('.slide');
const total = slides.length;

function showSlide(index) {
  slides.forEach((slide, i) => {
    slide.classList.toggle('active', i === index);
  });
}

function nextSlide() {
  current = (current + 1) % total;
  showSlide(current);
}

function prevSlide() {
  current = (current - 1 + total) % total;
  showSlide(current);
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelector('.next').addEventListener('click', nextSlide);
  document.querySelector('.prev').addEventListener('click', prevSlide);
  setInterval(nextSlide, 5000);
  showSlide(current);
});
</script>
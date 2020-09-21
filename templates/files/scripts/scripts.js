window.onload = function() {
    let msg = document.getElementById("script-message");
    msg.style.display = "none";
    let loading = document.getElementById("loading-screen");
    this.sleep(2000);
    loading.style.display = "none";
};
// When the user scrolls down 50px from the top of the document, resize the header's font size
/*window.onscroll = function () { scrollFunction() };

function scrollFunction() {
  let logo = document.getElementById("logo")
  let logoHeight = logo.offsetHeight;
  if (document.body.scrollTop > logoHeight - 200 || document.documentElement.scrollTop > logoHeight - 200) {
    document.getElementById("header-container").classList.add("white")
  } else {
    document.getElementById("header-container").classList.remove("white")
  }

  let end = document.getElementById("end")
  let top = end.offsetTop;
  if (document.body.scrollTop > top - 200 || document.documentElement.scrollTop > top - 200) {
    document.getElementById("end").classList.add("scrolled")
  } else {
    document.getElementById("end").classList.remove("scrolled")
  }
}*/

function sleep(milliseconds) {
    const date = Date.now();
    let currentDate = null;
    do {
        currentDate = Date.now();
    } while (currentDate - date < milliseconds);
}
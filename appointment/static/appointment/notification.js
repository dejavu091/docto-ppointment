document.addEventListener('DOMContentLoaded', function () {
  const msgs = document.querySelector('.messages');
  if (!msgs) return;

  // Give users time to read, then add a class that fades and collapses the messages
  setTimeout(function () {
    msgs.classList.add('fade-out');
    // remove from DOM after transition completes
    setTimeout(function () { if (msgs.parentNode) msgs.parentNode.removeChild(msgs); }, 600);
  }, 5000);
});

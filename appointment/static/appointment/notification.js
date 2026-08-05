document.addEventListener('DOMContentLoaded', function () {
  const msgs = document.querySelector('.messages');
  const matchSummary = document.getElementById('appointment-match-summary');
  const matchClose = document.querySelector('.match-summary-close');

  if (msgs) {
    setTimeout(function () {
      msgs.classList.add('fade-out');
      setTimeout(function () { if (msgs.parentNode) msgs.parentNode.removeChild(msgs); }, 600);
    }, 5000);
  }

  if (matchSummary && matchClose) {
    matchClose.addEventListener('click', function () {
      matchSummary.style.display = 'none';
    });
  }
});

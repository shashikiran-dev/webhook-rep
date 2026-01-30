function formatEvent(event) {
  const date = new Date(event.timestamp).toUTCString();

  if (event.action === 'push') {
    return `${event.author} pushed to ${event.to_branch} on ${date}`;
  }

  if (event.action === 'pull_request') {
    return `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${date}`;
  }

  if (event.action === 'merge') {
    return `${event.author} merged branch ${event.from_branch} to ${event.to_branch} on ${date}`;
  }
}

function loadEvents() {
  fetch('/events')
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('events');
      list.innerHTML = '';
      data.forEach(e => {
        const li = document.createElement('li');
        li.textContent = formatEvent(e);
        list.appendChild(li);
      });
    });
}

loadEvents();
setInterval(loadEvents, 15000);

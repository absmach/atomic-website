// Progressive enhancement: every solution remains visible without JavaScript.
const filters = document.querySelector('.solution-filters');
if (filters) {
  const buttons = [...filters.querySelectorAll('[data-solution-filter]')];
  const cards = [...document.querySelectorAll('[data-solution-category]')];
  const status = document.getElementById('solution-filter-status');
  filters.hidden = false;
  buttons.forEach(button => button.addEventListener('click', () => {
    const category = button.dataset.solutionFilter;
    buttons.forEach(filter => filter.setAttribute('aria-pressed', String(filter === button)));
    cards.forEach(card => {
      card.hidden = category !== 'all' && card.dataset.solutionCategory !== category;
    });
    const count = cards.filter(card => !card.hidden).length;
    status.textContent = `${count} solutions shown for ${button.textContent.toLowerCase()}.`;
  }));
}

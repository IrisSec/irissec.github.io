document.addEventListener('DOMContentLoaded', function() {
  var codeBlocks = document.querySelectorAll('div.highlighter-rouge');

  codeBlocks.forEach(function(codeBlock) {
    var expandButton = createExpandButton();
    codeBlock.children[0].appendChild(expandButton);

    var content = codeBlock.querySelector('pre');
    var isExpanded = false;

    codeBlock.classList.add('code-block');
    expandButton.style.display = 'inline';
    
    if (content.clientHeight <= 300) {
      expandButton.style.display = 'none';
      codeBlock.classList.add('expanded');
    } else {
      expandButton.addEventListener('click', function() {
        if (isExpanded) {
          codeBlock.classList.remove('expanded');
          expandButton.innerText = 'Expand';
        } else {
          codeBlock.classList.add('expanded');
          expandButton.innerText = 'Collapse';
        }
      
        isExpanded = !isExpanded;
      });
    }

  });
});

function createExpandButton() {
  var button = document.createElement('button');
  button.className = 'expand-button';
  button.innerHTML = 'Expand';
  return button;
}
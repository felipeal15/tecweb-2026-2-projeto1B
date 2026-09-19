function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Escolhe uma variação (cor/rotação) a partir do id da anotação, para que um
// mesmo card mantenha sempre a mesma aparência entre um reload e outro.
function pickVariant(card, quantidade) {
  const id = parseInt(card.dataset.id, 10);
  if (Number.isNaN(id)) {
    return getRandomInt(1, quantidade);
  }
  return (id % quantidade) + 1;
}

function autoResize(textarea) {
  textarea.style.height = "auto";
  textarea.style.height = textarea.scrollHeight + "px";
}

document.addEventListener("DOMContentLoaded", function () {
  // Faz textarea aumentar a altura automaticamente
  // Fonte: https://www.geeksforgeeks.org/how-to-create-auto-resize-textarea-using-javascript-jquery/
  let textareas = document.getElementsByClassName("autoresize");
  for (let i = 0; i < textareas.length; i++) {
    let textarea = textareas[i];
    textarea.addEventListener(
      "input",
      function () {
        autoResize(this);
      },
      false
    );
    // Na tela de edição o textarea já vem preenchido, então ajusta na carga.
    autoResize(textarea);
  }

  // Aplica as classes de cor e rotação dos cards
  let cards = document.getElementsByClassName("card");
  for (let i = 0; i < cards.length; i++) {
    let card = cards[i];
    card.className += ` card-color-${pickVariant(
      card,
      5
    )} card-rotation-${pickVariant(card, 11)}`;
  }
});

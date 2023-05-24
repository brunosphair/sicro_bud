$(document).ready(function() {
    $('#add-row').click(function() {
      var csrftoken = getCookie('csrftoken');  // Obtenha o valor do token CSRF do cookie
  
      $.ajax({
        url: 'http://127.0.0.1:8000/teste/obra/adicionar_linha/', 
        type: 'POST',
        dataType: 'json',
        headers: {'X-CSRFToken': csrftoken},  // Envie o token CSRF como um cabeçalho
        success: function(data) {
            if (data.success) {
                var newRow = '<tr><td contenteditable="true">' + data.coluna1 + '</td><td contenteditable="true">' + data.coluna2 + '</td></tr>';
                $('#my-table tbody').append(newRow);
                enableTableEditability(); // Habilitar edição da tabela
          }
        }
      });
    });
  });
  
  function enableTableEditability() {
    $('#my-table td').click(function() {
      // Remover classe de destaque de outras células
      $('#my-table td').removeClass('highlight');

      // Adicionar classe de destaque na célula clicada
      $(this).addClass('highlight');
    });
  };  
  // Função auxiliar para obter o valor do token CSRF do cookie
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
  $(document).ready(function() {
    $('[id^=search-input]').autocomplete({
      source: '{% url 'autocompletar_lista' %}',
      minLength: 1
    });
  });
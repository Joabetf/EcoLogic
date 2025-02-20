function atualizarSensores() {
    fetch('/api/sensores')
        .then(response => response.json())
        .then(data => {
            document.getElementById('luminosidade').textContent = data.luminosidade;
            document.getElementById('temperatura').textContent = data.temperatura;
            document.getElementById('corrente').textContent = data.corrente;
        })
        .catch(error => console.error("Erro ao buscar os sensores:", error));
}

setInterval(atualizarSensores, 2000);  // Atualiza a cada 2 segundos

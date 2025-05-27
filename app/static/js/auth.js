document.addEventListener('DOMContentLoaded', async function () {
    // Recupera o token armazenado no localStorage
    const token = localStorage.getItem('jwt');
    console.log(token);  // Verifique se o token está correto

    if (token) {
        try {
            const url = window.location.pathname; // Usa o caminho da URL atual

            const response = await fetch(url, {
                method: 'GET', // Ou POST, dependendo da requisição
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`  // Envia o token no cabeçalho
                },
            });
            console.log(response)
            if (response.ok) {
                const data = await response.json();
                console.log('Dados recebidos:', data); // Exibe os dados
            } else {
                const errorData = await response.json();
                console.log('Erro ao fazer requisição:', errorData.message);
            }
        } catch (error) {
           // console.error('Erro na requisição:', error);
        }
    } else {
        console.log('Token não encontrado. Redirecionando para login...');
        window.location.href = '/login'; // Redireciona para a página de login
    }
});
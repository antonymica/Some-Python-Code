document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const downloadBtn = document.getElementById('download-btn');
    const resultsDiv = document.getElementById('results');
    const passwordList = document.getElementById('password-list');
    
    generateBtn.addEventListener('click', generatePasswords);
    downloadBtn.addEventListener('click', downloadPasswords);
    
    function generatePasswords() {
        // Récupérer les paramètres du formulaire
        const count = document.getElementById('count').value;
        const length = document.getElementById('length').value;
        const uppercase = document.getElementById('uppercase').checked;
        const numbers = document.getElementById('numbers').checked;
        const specialChars = document.getElementById('special-chars').checked;
        const baseWordsInput = document.getElementById('base-words').value;
        
        // Séparer les mots de base
        const base_words = baseWordsInput.split(',')
            .map(word => word.trim())
            .filter(word => word.length > 0);
        
        // Afficher un indicateur de chargement
        generateBtn.disabled = true;
        generateBtn.textContent = 'Génération en cours...';
        
        // Envoyer la requête au serveur
        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                count: count,
                length: length,
                uppercase: uppercase,
                numbers: numbers,
                special_chars: specialChars,
                base_words: baseWordsInput
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPasswords(data.passwords, base_words);
            } else {
                alert('Erreur: ' + data.error);
            }
        })
        .catch(error => {
            alert('Une erreur est survenue: ' + error);
        })
        .finally(() => {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Générer des Mots de Passe';
        });
    }
    
    function displayPasswords(passwords, baseWords) {
        // Effacer les résultats précédents
        passwordList.innerHTML = '';
        
        // Afficher chaque mot de passe
        passwords.forEach((password, index) => {
            const passwordItem = document.createElement('div');
            passwordItem.className = 'password-item';
            
            // Mettre en évidence les mots de base dans le mot de passe
            let highlightedPassword = password;
            baseWords.forEach(word => {
                const regex = new RegExp(word, 'gi');
                highlightedPassword = highlightedPassword.replace(
                    regex, 
                    match => `<span class="base-word">${match}</span>`
                );
            });
            
            passwordItem.innerHTML = `
                <span>${index + 1}. ${highlightedPassword}</span>
                <button class="copy-btn" data-password="${password}">Copier</button>
            `;
            passwordList.appendChild(passwordItem);
        });
        
        // Ajouter les écouteurs d'événements pour les boutons de copie
        document.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const password = this.getAttribute('data-password');
                navigator.clipboard.writeText(password).then(() => {
                    const originalText = this.textContent;
                    this.textContent = 'Copié!';
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                });
            });
        });
        
        // Afficher la section des résultats
        resultsDiv.classList.remove('hidden');
    }
    
    function downloadPasswords() {
        // Récupérer tous les mots de passe
        const passwords = Array.from(document.querySelectorAll('.password-item span'))
            .map(span => {
                // Retirer les numéros et le HTML de mise en forme
                const text = span.textContent || span.innerText;
                return text.replace(/^\d+\.\s/, '').replace(/\s/g, '');
            });
        
        // Envoyer la requête au serveur pour télécharger
        fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                passwords: passwords
            }),
        })
        .then(response => {
            if (response.ok) return response.blob();
            throw new Error('Erreur lors du téléchargement');
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'wifi_passwords.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            alert('Erreur lors du téléchargement: ' + error.message);
        });
    }
});
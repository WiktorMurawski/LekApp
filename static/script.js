async function submitQuery() {
    const inputField = document.getElementById('textInput')
    const text = inputField.value;
    if (text == "")
        return;
    loadData(text);
    inputField.value = "";
}

async function loadData(query) {
    const table = document.getElementById('resultsTable');
    table.hidden = true;
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');

    const url = `/search?query=${encodeURIComponent(query)}`;

    try {
        const res = await fetch(url);
        const result = await res.json();

        const columns = result.columns;
        const data = result.rows;

        if (data.length === 0) {
            document.getElementById('label').innerHTML = "Nic nie znaleziono";
            return;
        }

        // Headers
        thead.innerHTML = '<tr>' + columns.map(col => `<th>${col}</th>`).join('') + '</tr>';

        // Cells
        tbody.innerHTML = data.map(row =>
            '<tr>' + columns.map(col => {
                const cellContent = row[col] ?? '';
                return `<td><div class="cell-content">${cellContent}</div></td>`;
            }).join('') + '</tr>'
        ).join('');

        table.hidden = false;
        const message = result.length < 1000 ? `Znaleziono ${result.length} wyników` : `Znaleziono >1000 wyników`;
        document.getElementById('label').innerHTML = message;
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

document.getElementById("textInput").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        submitQuery();
    }
});
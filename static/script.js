async function submitQuery() {
    const inputField = document.getElementById('textInput')
    const searchType = document.getElementById('searchType').value;
    const text = inputField.value;
    if (text == "")
        return;
    loadData(text, searchType);
    inputField.value = "";
}

async function loadData(query, type) {
    const table = document.getElementById('resultsTable');
    table.hidden = true;
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');

    // const url = `/search?query=${encodeURIComponent(query)}`;
    const url = `/search?query=${encodeURIComponent(query)}&type=${encodeURIComponent(type)}`;

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
        // const message = result.length < 1000 ? `Znaleziono ${result.length} wyników` : `Znaleziono >1000 wyników`;
        let message = "";
        if (result.length == 1000)
            message = "Znaleziono >1000 wyników";
        else if (result.length == 1)
            message = "Znaleziono 1 wynik"
        else if (result.length % 10 >= 2 && result.length % 10 <= 4)
            message = `Znaleziono ${result.length} wyniki`;
        else
            message = `Znaleziono ${result.length} wyników`;

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
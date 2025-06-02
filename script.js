document.getElementById("rankForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const rank = parseInt(document.getElementById("rank").value);
    const category = document.getElementById("category").value.trim();
    const institute = document.getElementById("institute").value.trim().toLowerCase();
  
    Papa.parse("data.csv", {
      download: true,
      header: true,
      complete: function(results) {
        const data = results.data;
        const filtered = data.filter(row => {
          const rowCategory = row.Category.trim();
          const rowInstitute = row.Institute.toLowerCase().trim();
          const closingRank = parseInt(row.ClosingRank);
          
          return (
            rowCategory === category &&
            closingRank >= rank &&
            (institute === "" || rowInstitute.includes(institute))
          );
        });
  
        displayResults(filtered);
      }
    });
  });
  
  function displayResults(results) {
    const container = document.getElementById("results");
    container.innerHTML = "<h2>Matching Branches:</h2>";
  
    if (results.length === 0) {
      container.innerHTML += "<p>No matching branches found.</p>";
      return;
    }
  
    const list = document.createElement("ul");
    results.forEach(row => {
      const item = document.createElement("li");
      item.textContent = `${row.Institute} - ${row.Branch} (Closing Rank: ${row.ClosingRank})`;
      list.appendChild(item);
    });
  
    container.appendChild(list);
  }
  
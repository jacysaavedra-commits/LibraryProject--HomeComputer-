(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const issueDateInput = document.querySelector('#id_issue_date');
        const returnDateInput = document.querySelector('#id_return_date');
        
        if (!issueDateInput || !returnDateInput) return;
        
        function calculateReturnDate() {
            const issueDate = issueDateInput.value;
            
            if (!issueDate) {
                returnDateInput.value = '';
                return;
            }
            
            // Parse the date string (format: YYYY-MM-DD)
            const date = new Date(issueDate);
            
            if (isNaN(date.getTime())) {
                return;
            }
            
            // Add 14 days
            date.setDate(date.getDate() + 14);
            
            // Format as YYYY-MM-DD
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            
            const formattedDate = `${year}-${month}-${day}`;
            returnDateInput.value = formattedDate;
        }
        
        // Listen for changes on the issue_date field
        issueDateInput.addEventListener('change', calculateReturnDate);
    });
})();

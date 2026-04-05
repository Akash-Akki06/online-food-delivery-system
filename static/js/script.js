// Simple logging and basic interactions
console.log("Food Delivery App loaded successfully.");

document.addEventListener("DOMContentLoaded", () => {
    // Attach simple visual feedback for buttons when clicked
    const addButtons = document.querySelectorAll('.add-btn');
    
    addButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const originalText = this.innerText;
            this.innerText = 'Added!';
            this.style.backgroundColor = 'var(--primary-red)';
            this.style.color = 'var(--white)';
            
            setTimeout(() => {
                this.innerText = originalText;
                this.style.backgroundColor = 'transparent';
                this.style.color = 'var(--primary-red)';
            }, 2000);
        });
    });
});

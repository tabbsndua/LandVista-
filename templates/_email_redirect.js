document.addEventListener('click', function(e){
    const target = e.target.closest && e.target.closest('a');
    if(!target) return;
    const href = target.getAttribute('href') || '';
    if(href.toLowerCase().startsWith('mailto:')){
        const addr = href.slice(7).toLowerCase();
        if(addr === 'info@landvistaproperties.com'){
            e.preventDefault();
            // Redirect to contact page so users fill the form instead
            window.location.href = '/contact';
        }
    }
}, true);
$("#searchForm").on("submit",function(e){
    e.preventDefault();

    const name = $("#search").val().trim();

    window.location.href = `/Users/search/?name=${encodeURIComponent(name)}`;
});
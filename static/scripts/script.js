function createTable(headers, data) {
    $("table").empty()
    
    $(".tbl-header table").html(`
    <thead>
        <tr>
            <th>Rank</th>
        </tr>
    </thead>`)
    $(".tbl-content table").html(`
    <tbody>
    </tbody>`)
    

    for (const header of headers) {
        $("table thead tr").append(`<th>${header}</th>`)
    }

    for (const [i, row] of data.entries()) {
        $("table tbody").append(`
            <tr>
                <td>
                    <h3>${i}</h3>
                </td>
            </tr>`)

        for (const cell of Object.values(row)) {
            $("table tbody tr").eq(i).append(`
                <td>${cell}</td>`)
        }
    }
}

function autofit() {
    const width = $(".tbl-header").css("width")
    $(".tbl-content").css("width", width)
    $("body").css("width", width)
    $("body").css("bacvground", `linear-gradient(to right, #25c481, ${width}, #25b7c4)`)
}

createTable(headers, stocksData)

$(document).ready(function () {
    autofit()
});

const checkboxes = $("nav ul li input")

$(window).on("load resize", function () {
    var scrollWidth = $('.tbl-content').width() - $('.tbl-content table').width();
    $('.tbl-header').css({ 'padding-right': scrollWidth });
}).resize();

$("nav ul li input#all").change(e => {
    checkboxes.prop("checked", !checkboxes.prop("checked"))
})

$("nav button").click(function () {

    $("nav ul").toggleClass("show")

    checkboxes.change(function (e) {
        const headers = []

        const checked = $("nav ul li input:checked")

        checked.each(i => {
            const id = checked.eq(i).prop("id")

            if (id !== "all") {
                headers.push(id)
            }
        })

        const data = stocksData.map(stock => {
            const newStock = Object.entries(stock)
                .filter(([key]) => headers.includes(key))

            return Object.fromEntries(newStock)
        })

        createTable(headers, data)
        autofit()
    })
})
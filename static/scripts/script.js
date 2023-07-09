var columns = localStorage.getItem("columns")

if (columns) columns = columns.split(", ")
else columns = []

if (columns.length === 0) {
    columns = headers
    localStorage.setItem("columns", headers)
}

const checkboxes = $("nav ul li input")



function createTable(headersList) {
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
    

    for (const header of headersList) {
        $("table thead tr").append(`<th>${header}</th>`)
    }

    for (const [i, row] of stocksData.entries()) {
        $("table tbody").append(`
            <tr>
                <td>
                    <h3>${i + 1}</h3>
                </td>
            </tr>`)
        for (const [ header, cell ] of Object.entries(row)) {

            if (headersList.includes(header)) {

                var cellHTML = `
                    <td>${cell}</td>`

                if (header === "Symbol") {
                    cellHTML = `
                    <td><a href="https://stockanalysis.com/stocks/${cell}/forecast/" target="_blank" rel="noopener noreferrer">${cell}</a></td>`
                }

                $("table tbody tr").eq(i).append(cellHTML)

            }

        }
    }
}

function autofit() {
    const width = $(".tbl-header").css("width")
    $(".tbl-content").css("width", width)
    $("body").css("width", width)
    $("body").css("bacvground", `linear-gradient(to right, #25c481, ${width}, #25b7c4)`)
}









$(document).ready(function () {
    const currHeaders = headers.filter(header => columns.includes(header))

    for (const column of columns) {
        document.getElementById(column).checked = true
    }

    createTable(currHeaders)
    autofit()
});

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

        localStorage.setItem("columns", headers.join(", "))
        createTable(headers)
        autofit()
    })
})
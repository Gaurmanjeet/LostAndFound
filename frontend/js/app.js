const API_URL = "http://127.0.0.1:5000";


// ======================================================
// COMMON HELPERS
// ======================================================

function escapeHTML(value) {
    if (value === null || value === undefined) return "";

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}


function showMessage(message) {
    alert(message);
}


function getImageURL(imagePath) {

    if (!imagePath) {
        return "";
    }

    if (
        imagePath.startsWith("http://") ||
        imagePath.startsWith("https://")
    ) {
        return imagePath;
    }

    if (imagePath.startsWith("/")) {
        return `${API_URL}${imagePath}`;
    }

    return `${API_URL}/${imagePath}`;
}


async function apiRequest(endpoint, options = {}) {

    const config = {
        credentials: "include",
        ...options
    };

    const response = await fetch(
        `${API_URL}${endpoint}`,
        config
    );

    let data;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            `Server returned invalid response (${response.status})`
        );
    }

    if (!response.ok) {
        throw new Error(
            data.message ||
            `Request failed with status ${response.status}`
        );
    }

    return data;
}


function formatDate(dateValue) {

    if (!dateValue) {
        return "N/A";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return dateValue;
    }

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}


// ======================================================
// LOGOUT
// ======================================================

async function logoutUser() {

    try {

        await apiRequest(
            "/api/logout",
            {
                method: "POST"
            }
        );

    } catch (error) {

        console.error("Logout error:", error);

    } finally {

        window.location.href = "index.html";

    }
}


window.logoutUser = logoutUser;


async function adminLogout() {
    await logoutUser();
}


window.adminLogout = adminLogout;


// ======================================================
// REGISTER
// ======================================================

function setupRegister() {

    const form = document.getElementById("registerForm");

    if (!form) return;


    form.addEventListener("submit", async function (event) {

        event.preventDefault();


        const name =
            document.getElementById("registerName")?.value.trim();

        const email =
            document.getElementById("registerEmail")?.value.trim();

        const password =
            document.getElementById("registerPassword")?.value;

        const confirmPassword =
            document.getElementById("confirmPassword")?.value;


        if (!name || !email || !password || !confirmPassword) {

            showMessage("Please fill all fields.");

            return;
        }


        if (password.length < 6) {

            showMessage(
                "Password must contain at least 6 characters."
            );

            return;
        }


        if (password !== confirmPassword) {

            showMessage("Passwords do not match.");

            return;
        }


        try {

            const result = await apiRequest(
                "/api/register",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        full_name: name,
                        email: email,
                        password: password
                    })
                }
            );


            showMessage(
                result.message ||
                "Registration successful."
            );


            window.location.href = "login.html";


        } catch (error) {

            console.error("Register error:", error);

            showMessage(error.message);

        }

    });

}


// ======================================================
// LOGIN
// ======================================================

function setupLogin() {

    const form = document.getElementById("loginForm");

    if (!form) return;


    form.addEventListener("submit", async function (event) {

        event.preventDefault();


        const email =
            document.getElementById("loginEmail")?.value.trim();

        const password =
            document.getElementById("loginPassword")?.value;


        if (!email || !password) {

            showMessage(
                "Please enter email and password."
            );

            return;
        }


        try {

            const result = await apiRequest(
                "/api/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );


            if (!result.success) {

                showMessage(
                    result.message ||
                    "Login failed."
                );

                return;
            }


            const user = result.user || {};

            if (user.role === "admin") {

                window.location.href = "admin.html";

            } else {

                window.location.href = "dashboard.html";

            }


        } catch (error) {

            console.error("Login error:", error);

            showMessage(error.message);

        }

    });

}


// ======================================================
// AUTH CHECK
// ======================================================

async function getCurrentUser() {

    try {

        const result = await apiRequest(
            "/api/me"
        );

        return result.user || null;

    } catch (error) {

        return null;

    }

}


// ======================================================
// ITEM CARD
// ======================================================

function createItemCard(item) {

    const imageURL = getImageURL(
        item.image_path
    );


    const status =
        item.status || "active";


    const statusClass =
        status === "returned"
            ? "success"
            : status === "closed"
                ? "secondary"
                : status === "claimed"
                    ? "warning"
                    : "primary";


    return `
        <div class="col-md-6 col-lg-4">

            <div class="card h-100 shadow-sm border-0">

                ${
                    imageURL
                        ? `
                            <img
                                src="${escapeHTML(imageURL)}"
                                class="card-img-top"
                                alt="${escapeHTML(item.title)}"
                                style="height:220px; object-fit:cover;"
                            >
                          `
                        : `
                            <div
                                class="d-flex align-items-center justify-content-center bg-light"
                                style="height:220px;"
                            >
                                <i
                                    class="fa-solid fa-image fa-3x text-muted"
                                ></i>
                            </div>
                          `
                }


                <div class="card-body">

                    <div class="d-flex justify-content-between align-items-start mb-2">

                        <h5 class="card-title mb-0">
                            ${escapeHTML(item.title)}
                        </h5>

                        <span class="badge text-bg-${statusClass}">
                            ${escapeHTML(status)}
                        </span>

                    </div>


                    <p class="mb-1">
                        <strong>Category:</strong>
                        ${escapeHTML(item.category)}
                    </p>


                    <p class="mb-1">
                        <strong>Location:</strong>
                        ${escapeHTML(item.location)}
                    </p>


                    <p class="mb-2">
                        <strong>Date:</strong>
                        ${formatDate(item.item_date)}
                    </p>


                    <p class="text-muted small">
                        ${escapeHTML(
                            item.description || "No description available."
                        )}
                    </p>


                    <a
                        href="item-details.html?id=${encodeURIComponent(item.id)}"
                        class="btn btn-primary w-100"
                    >
                        View Details
                    </a>

                </div>

            </div>

        </div>
    `;
}


// ======================================================
// LOAD ITEMS
// ======================================================

async function fetchItems(type = "") {

    let endpoint = "/api/items";

    if (type) {

        endpoint +=
            `?type=${encodeURIComponent(type)}`;

    }


    const result = await apiRequest(endpoint);

    return result.items || [];

}


// ======================================================
// LOST / FOUND LISTING
// ======================================================

async function loadListingPage(type) {

    const container =
        document.getElementById(
            type === "lost"
                ? "lostItemsContainer"
                : "foundItemsContainer"
        );


    if (!container) return;


    try {

        let items = await fetchItems(type);


        const searchInput =
            document.getElementById(
                type === "lost"
                    ? "lostSearch"
                    : "foundSearch"
            );


        const categoryInput =
            document.getElementById(
                type === "lost"
                    ? "lostCategory"
                    : "foundCategory"
            );


        const locationInput =
            document.getElementById(
                type === "lost"
                    ? "lostLocation"
                    : "foundLocation"
            );


        const render = function () {

            const search =
                searchInput?.value
                    .trim()
                    .toLowerCase() || "";


            const category =
                categoryInput?.value
                    .trim()
                    .toLowerCase() || "";


            const location =
                locationInput?.value
                    .trim()
                    .toLowerCase() || "";


            const filtered =
                items.filter(item => {

                    const searchable = [
                        item.title,
                        item.category,
                        item.description,
                        item.location
                    ]
                        .filter(Boolean)
                        .join(" ")
                        .toLowerCase();


                    const matchesSearch =
                        !search ||
                        searchable.includes(search);


                    const matchesCategory =
                        !category ||
                        String(item.category || "")
                            .toLowerCase()
                            .includes(category);


                    const matchesLocation =
                        !location ||
                        String(item.location || "")
                            .toLowerCase()
                            .includes(location);


                    return (
                        matchesSearch &&
                        matchesCategory &&
                        matchesLocation
                    );

                });


            if (filtered.length === 0) {

                container.innerHTML = `
                    <div class="col-12">

                        <div class="text-center py-5">

                            <i
                                class="fa-solid fa-box-open fa-3x text-muted"
                            ></i>

                            <h4 class="mt-3">
                                No items found
                            </h4>

                            <p class="text-muted">
                                Try another search or filter.
                            </p>

                        </div>

                    </div>
                `;

                return;
            }


            container.innerHTML =
                filtered.map(createItemCard).join("");

        };


        render();


        const button =
            document.getElementById(
                type === "lost"
                    ? "lostSearchButton"
                    : "foundSearchButton"
            );


        button?.addEventListener(
            "click",
            render
        );


        searchInput?.addEventListener(
            "keydown",
            event => {

                if (event.key === "Enter") {
                    render();
                }

            }
        );


        categoryInput?.addEventListener(
            "change",
            render
        );


        locationInput?.addEventListener(
            "change",
            render
        );


    } catch (error) {

        console.error(
            `${type} items error:`,
            error
        );


        container.innerHTML = `
            <div class="col-12">

                <div class="alert alert-danger">

                    Unable to load ${type} items.

                    <br>

                    <small>
                        ${escapeHTML(error.message)}
                    </small>

                </div>

            </div>
        `;

    }

}


// ======================================================
// HOME SEARCH
// ======================================================

async function setupHomeSearch() {

    const button =
        document.getElementById(
            "homeSearchButton"
        );


    if (!button) return;


    const searchInput =
        document.getElementById(
            "homeSearch"
        );


    const categoryInput =
        document.getElementById(
            "homeCategory"
        );


    const locationInput =
        document.getElementById(
            "homeLocation"
        );


    let resultsContainer =
        document.getElementById(
            "homeSearchResults"
        );


    if (!resultsContainer) {

        resultsContainer =
            document.createElement("div");

        resultsContainer.id =
            "homeSearchResults";

        resultsContainer.className =
            "container mt-4 mb-5";


        const searchSection =
            document.querySelector(
                ".search-section"
            );


        if (searchSection) {

            searchSection.after(
                resultsContainer
            );

        } else {

            document.body.appendChild(
                resultsContainer
            );

        }

    }


    async function performSearch() {

        const search =
            searchInput?.value
                .trim()
                .toLowerCase() || "";


        const category =
            categoryInput?.value
                .trim()
                .toLowerCase() || "";


        const location =
            locationInput?.value
                .trim()
                .toLowerCase() || "";


        resultsContainer.innerHTML = `
            <div class="text-center py-4">

                <i
                    class="fa-solid fa-spinner fa-spin fa-2x"
                ></i>

                <p class="mt-2">
                    Searching...
                </p>

            </div>
        `;


        try {

            const result =
                await apiRequest(
                    "/api/items"
                );


            const items =
                result.items || [];


            const filtered =
                items.filter(item => {

                    const searchable = [
                        item.title,
                        item.category,
                        item.description,
                        item.location,
                        item.item_type
                    ]
                        .filter(Boolean)
                        .join(" ")
                        .toLowerCase();


                    return (
                        (!search ||
                            searchable.includes(search)) &&

                        (!category ||
                            String(item.category || "")
                                .toLowerCase()
                                .includes(category)) &&

                        (!location ||
                            String(item.location || "")
                                .toLowerCase()
                                .includes(location))
                    );

                });


            if (filtered.length === 0) {

                resultsContainer.innerHTML = `
                    <div class="alert alert-info">

                        <i class="fa-solid fa-circle-info me-2"></i>

                        No matching items found.

                    </div>
                `;

                return;
            }


            resultsContainer.innerHTML = `

                <div class="mb-3">

                    <h3>
                        Search Results
                    </h3>

                    <p class="text-muted">
                        ${filtered.length} item(s) found
                    </p>

                </div>


                <div class="row g-4">

                    ${filtered
                        .map(createItemCard)
                        .join("")}

                </div>
            `;


            resultsContainer.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });


        } catch (error) {

            console.error(
                "Home search error:",
                error
            );


            resultsContainer.innerHTML = `
                <div class="alert alert-danger">

                    Unable to search items.

                    <br>

                    <small>
                        ${escapeHTML(error.message)}
                    </small>

                </div>
            `;

        }

    }


    button.addEventListener(
        "click",
        performSearch
    );


    searchInput?.addEventListener(
        "keydown",
        event => {

            if (event.key === "Enter") {
                performSearch();
            }

        }
    );

}


// ======================================================
// ITEM DETAILS
// ======================================================

async function loadItemDetails() {

    const titleElement =
        document.getElementById(
            "detailTitle"
        );


    if (!titleElement) return;


    const itemId =
        getQueryParam("id");


    if (!itemId) {

        showMessage(
            "Item ID is missing."
        );

        return;
    }


    try {

        const result =
            await apiRequest(
                `/api/items/${itemId}`
            );


        const item =
            result.item;


        if (!item) {

            throw new Error(
                "Item not found."
            );

        }


        const imageElement =
            document.getElementById(
                "detailImage"
            );


        const placeholder =
            document.getElementById(
                "noImagePlaceholder"
            );


        if (
            item.image_path &&
            imageElement
        ) {

            imageElement.src =
                getImageURL(
                    item.image_path
                );

            imageElement.style.display =
                "block";


            if (placeholder) {
                placeholder.style.display =
                    "none";
            }

        }


        titleElement.textContent =
            item.title || "";


        const category =
            document.getElementById(
                "detailCategory"
            );

        if (category) {
            category.textContent =
                item.category || "N/A";
        }


        const location =
            document.getElementById(
                "detailLocation"
            );

        if (location) {
            location.textContent =
                item.location || "N/A";
        }


        const date =
            document.getElementById(
                "detailDate"
            );

        if (date) {
            date.textContent =
                formatDate(
                    item.item_date
                );
        }


        const description =
            document.getElementById(
                "detailDescription"
            );

        if (description) {
            description.textContent =
                item.description || "No description.";
        }


        const reporter =
            document.getElementById(
                "detailReporter"
            );

        if (reporter) {
            reporter.textContent =
                item.full_name || "Unknown";
        }


        const status =
            document.getElementById(
                "detailStatus"
            );

        if (status) {
            status.textContent =
                item.status || "active";
        }

const claimButton = document.getElementById("claimItemButton");
const currentUser = await getCurrentUser();

if (
    claimButton &&
    currentUser?.role !== "admin" &&
    item.item_type === "found" &&
    item.status === "active"
) {
    claimButton.style.display = "inline-block";

    claimButton.onclick = async () => {
        await submitClaim(item.id);
    };
} else if (claimButton) {
    claimButton.style.display = "none";
}

    } catch (error) {

        console.error(
            "Item details error:",
            error
        );

        showMessage(
            error.message
        );

    }

}


// ======================================================
// CLAIM
// ======================================================

async function submitClaim(itemId) {

    const description =
        prompt(
            "Why do you believe this item belongs to you?"
        );


    if (!description) {
        return;
    }


    if (description.trim().length < 10) {

        showMessage(
            "Please provide at least 10 characters."
        );

        return;
    }


    try {

        const result =
            await apiRequest(
                "/api/claims",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        item_id: itemId,
                        claim_description:
                            description.trim()
                    })
                }
            );


        showMessage(
    "Claim request submitted successfully. It is pending admin approval.",
    "success"
);

    } catch (error) {

        console.error(
            "Claim error:",
            error
        );

        showMessage(
            error.message
        );

    }

}


window.submitClaim = submitClaim;


// ======================================================
// DASHBOARD
// ======================================================

async function loadDashboard() {

    const lostCount =
        document.getElementById(
            "lostCount"
        );


    const foundCount =
        document.getElementById(
            "foundCount"
        );


    const matchCount =
        document.getElementById(
            "matchCount"
        );


    const claimCount =
        document.getElementById(
            "claimCount"
        );


    if (
        !lostCount &&
        !foundCount &&
        !matchCount &&
        !claimCount
    ) {
        return;
    }


    try {

        const result =
            await apiRequest(
                "/api/dashboard"
            );


        console.log(
            "Dashboard API:",
            result
        );


        if (!result.success) {

            throw new Error(
                result.message ||
                "Dashboard request failed."
            );

        }


        const stats =
            result.stats || result;


        const lost =
            stats.lost ??
            stats.lost_count ??
            result.lost ??
            0;


        const found =
            stats.found ??
            stats.found_count ??
            result.found ??
            0;


        const matches =
            stats.matches ??
            stats.match_count ??
            result.matches_count ??
            result.matches ??
            0;


        const claims =
            stats.claims ??
            stats.claim_count ??
            result.claims ??
            0;


        if (lostCount) {
            lostCount.textContent = lost;
        }


        if (foundCount) {
            foundCount.textContent = found;
        }


        if (matchCount) {
            matchCount.textContent = matches;
        }


        if (claimCount) {
            claimCount.textContent = claims;
        }


        // --------------------------------------------------
        // USER NAME
        // --------------------------------------------------

        const user =
            result.user || {};


        const userName =
            user.full_name ||
            user.name ||
            "";


        const dashboardUserName =
            document.getElementById(
                "dashboardUserName"
            );


        const navUserName =
            document.getElementById(
                "navUserName"
            );


        if (dashboardUserName && userName) {
            dashboardUserName.textContent =
                userName;
        }


        if (navUserName && userName) {
            navUserName.textContent =
                userName;
        }


        // --------------------------------------------------
        // RECENT REPORTS
        // --------------------------------------------------

        const recentContainer =
            document.getElementById(
                "recentReports"
            );


        if (recentContainer) {

            const reports =
                result.recent_reports ||
                result.recentReports ||
                [];


            if (reports.length === 0) {

                recentContainer.innerHTML = `
                    <div class="text-center py-4">

                        <i
                            class="fa-solid fa-box-open fa-2x text-muted"
                        ></i>

                        <p class="mt-3 text-muted">
                            No reports yet.
                        </p>

                    </div>
                `;

            } else {

                recentContainer.innerHTML =
                    reports
                        .map(createDashboardReport)
                        .join("");

            }

        }


        // --------------------------------------------------
        // MATCHES
        // --------------------------------------------------

        await loadDashboardMatches();


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );


        if (lostCount) {
            lostCount.textContent = "0";
        }


        if (foundCount) {
            foundCount.textContent = "0";
        }


        if (matchCount) {
            matchCount.textContent = "0";
        }


        if (claimCount) {
            claimCount.textContent = "0";
        }


        const recentContainer =
            document.getElementById(
                "recentReports"
            );


        if (recentContainer) {

            recentContainer.innerHTML = `
                <div class="alert alert-danger">

                    <strong>
                        Dashboard could not be loaded.
                    </strong>

                    <br>

                    <small>
                        ${escapeHTML(error.message)}
                    </small>

                </div>
            `;

        }


        const matchContainer =
            document.getElementById(
                "possibleMatches"
            );


        if (matchContainer) {

            matchContainer.innerHTML = `
                <div class="alert alert-danger">

                    Unable to load matches.

                    <br>

                    <small>
                        ${escapeHTML(error.message)}
                    </small>

                </div>
            `;

        }

    }

}


// ======================================================
// DASHBOARD REPORT CARD
// ======================================================

function createDashboardReport(item) {

    return `

        <div class="border-bottom py-3">

            <div class="d-flex justify-content-between">

                <div>

                    <h5 class="mb-1">

                        ${escapeHTML(
                            item.title
                        )}

                    </h5>


                    <p class="mb-1 text-muted">

                        ${escapeHTML(
                            item.item_type || ""
                        ).toUpperCase()}

                        ·

                        ${escapeHTML(
                            item.category || ""
                        )}

                    </p>


                    <small class="text-muted">

                        ${escapeHTML(
                            item.location || ""
                        )}

                        ·

                        ${formatDate(
                            item.item_date
                        )}

                    </small>

                </div>


                <a
                    href="item-details.html?id=${encodeURIComponent(item.id)}"
                    class="btn btn-sm btn-outline-primary align-self-center"
                >
                    View
                </a>

            </div>

        </div>

    `;

}


// ======================================================
// DASHBOARD MATCHES
// ======================================================

async function loadDashboardMatches() {

    const container =
        document.getElementById(
            "possibleMatches"
        );


    if (!container) return;


    try {

        const result =
            await apiRequest(
                "/api/matches"
            );


        const matches =
            result.matches || [];


        const matchCount =
            document.getElementById(
                "matchCount"
            );


        if (matchCount) {
            matchCount.textContent =
                matches.length;
        }


        if (matches.length === 0) {

            container.innerHTML = `
                <div class="text-center py-4">

                    <i
                        class="fa-solid fa-link-slash fa-2x text-muted"
                    ></i>

                    <p class="mt-3 text-muted">

                        No possible matches found yet.

                    </p>

                </div>
            `;

            return;
        }


        container.innerHTML =
            matches
                .map(createMatchCard)
                .join("");


    } catch (error) {

        console.error(
            "Matches error:",
            error
        );


        container.innerHTML = `
            <div class="alert alert-warning">

                Could not load possible matches.

                <br>

                <small>
                    ${escapeHTML(error.message)}
                </small>

            </div>
        `;

    }

}


// ======================================================
// MATCH CARD
// ======================================================

function createMatchCard(match) {

    const score =
        match.match_score ??
        match.score ??
        0;


    const lostTitle =
        match.lost_title ||
        match.lost_item_title ||
        "Lost item";


    const foundTitle =
        match.found_title ||
        match.found_item_title ||
        "Found item";


    return `

        <div class="border rounded p-3 mb-3">

            <div class="d-flex justify-content-between">

                <div>

                    <h5 class="mb-2">

                        ${escapeHTML(
                            lostTitle
                        )}

                        <i
                            class="fa-solid fa-arrow-right mx-2"
                        ></i>

                        ${escapeHTML(
                            foundTitle
                        )}

                    </h5>


                    <p class="mb-1">

                        <strong>
                            Match Score:
                        </strong>

                        ${escapeHTML(score)}%

                    </p>


                    ${
                        match.category
                            ? `
                                <p class="mb-1 text-muted">

                                    Category:
                                    ${escapeHTML(
                                        match.category
                                    )}

                                </p>
                              `
                            : ""
                    }


                    ${
                        match.location
                            ? `
                                <p class="mb-0 text-muted">

                                    Location:
                                    ${escapeHTML(
                                        match.location
                                    )}

                                </p>
                              `
                            : ""
                    }

                </div>


                ${
                    match.found_item_id
                        ? `
                            <a
                                href="item-details.html?id=${encodeURIComponent(
                                    match.found_item_id
                                )}"
                                class="btn btn-sm btn-primary align-self-center"
                            >
                                View
                            </a>
                          `
                        : ""
                }

            </div>

        </div>

    `;

}


// ======================================================
// MY CLAIMS
// ======================================================

async function loadMyClaims() {

    const container =
        document.getElementById(
            "myClaimsContainer"
        );


    if (!container) return;


    try {

        const result =
            await apiRequest(
                "/api/claims/my"
            );


        const claims =
            result.claims || [];


        if (claims.length === 0) {

            container.innerHTML = `
                <div class="text-center py-4">

                    <p class="text-muted">
                        You have not submitted any claims.
                    </p>

                </div>
            `;

            return;
        }


        container.innerHTML =
            claims.map(claim => `

                <div class="border rounded p-3 mb-3">

                    <h5>
                        ${escapeHTML(
                            claim.title ||
                            claim.item_title ||
                            "Claim"
                        )}
                    </h5>


                    <p class="mb-1">

                        Status:

                        <strong>
                            ${escapeHTML(
                                claim.status
                            )}
                        </strong>

                    </p>


                    <p class="mb-0 text-muted">

                        ${escapeHTML(
                            claim.claim_description ||
                            ""
                        )}

                    </p>

                </div>

            `).join("");


    } catch (error) {

        console.error(
            "Claims error:",
            error
        );


        container.innerHTML = `
            <div class="alert alert-danger">

                Unable to load claims.

            </div>
        `;

    }

}


// ======================================================
// ITEM REPORT FORM
// ======================================================

function setupItemForm(
    formId,
    titleId,
    categoryId,
    descriptionId,
    locationId,
    dateId,
    imageId,
    itemType
) {

    const form =
        document.getElementById(
            formId
        );


    if (!form) return;


    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const title =
                document.getElementById(
                    titleId
                )?.value.trim();


            const category =
                document.getElementById(
                    categoryId
                )?.value;


            const description =
                document.getElementById(
                    descriptionId
                )?.value.trim();


            const location =
                document.getElementById(
                    locationId
                )?.value.trim();


            const date =
                document.getElementById(
                    dateId
                )?.value;


            const image =
                document.getElementById(
                    imageId
                )?.files?.[0];


            if (
                !title ||
                !category ||
                !description ||
                !location ||
                !date
            ) {

                showMessage(
                    "Please fill all required fields."
                );

                return;
            }


            const formData =
                new FormData();


            formData.append(
                "title",
                title
            );


            formData.append(
                "category",
                category
            );


            formData.append(
                "description",
                description
            );


            formData.append(
                "location",
                location
            );


            formData.append(
                "item_date",
                date
            );


            formData.append(
                "item_type",
                itemType
            );


            if (image) {

                formData.append(
                    "image",
                    image
                );

            }


            try {

                const result =
                    await apiRequest(
                        "/api/items",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                showMessage(
                    result.message ||
                    "Item reported successfully."
                );


                window.location.href =
                    itemType === "lost"
                        ? "lost-items.html"
                        : "found-items.html";


            } catch (error) {

                console.error(
                    "Report item error:",
                    error
                );


                showMessage(
                    error.message
                );

            }

        }
    );

}


// ======================================================
// ADMIN DASHBOARD
// ======================================================

async function loadAdminDashboard() {

    const adminPage =
        document.getElementById(
            "adminPage"
        );


    if (!adminPage) return;


    try {

        const result =
            await apiRequest(
                "/api/admin/dashboard"
            );


        if (!result.success) {

            throw new Error(
                result.message ||
                "Unable to load admin dashboard."
            );

        }


        const stats =
            result.stats || result;


        setText(
            "totalUsers",
            stats.total_users ??
            stats.users ??
            0
        );


        setText(
            "totalItems",
            stats.total_items ??
            stats.items ??
            0
        );


        setText(
            "lostItems",
            stats.lost_items ??
            stats.lost ??
            0
        );


        setText(
            "foundItems",
            stats.found_items ??
            stats.found ??
            0
        );


        setText(
            "activeItems",
            stats.active_items ??
            stats.active ??
            0
        );


        setText(
            "returnedItems",
            stats.returned_items ??
            stats.returned ??
            0
        );


        setText(
            "pendingClaims",
            stats.pending_claims ??
            stats.pending ??
            0
        );


        setText(
            "approvedClaims",
            stats.approved_claims ??
            stats.approved ??
            0
        );


        setText(
            "rejectedClaims",
            stats.rejected_claims ??
            stats.rejected ??
            0
        );


        setText(
            "totalMatches",
            stats.total_matches ??
            stats.matches ??
            0
        );


        await loadAdminClaims();


    } catch (error) {

        console.error(
            "Admin dashboard error:",
            error
        );


        showMessage(
            error.message
        );

    }

}


function setText(id, value) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent =
            value ?? 0;

    }

}


// ======================================================
// ADMIN CLAIMS
// ======================================================

async function loadAdminClaims() {

    const container =
        document.getElementById(
            "adminClaimsContainer"
        );


    if (!container) return;


    try {

        const result =
            await apiRequest(
                "/api/admin/claims"
            );


        const claims =
            result.claims || [];


        if (claims.length === 0) {

            container.innerHTML = `
                <div class="text-center py-5">

                    <i
                        class="fa-solid fa-inbox fa-3x text-muted"
                    ></i>

                    <p class="mt-3 text-muted">
                        No claim requests found.
                    </p>

                </div>
            `;

            return;
        }


        container.innerHTML =
            claims.map(claim => `

                <div
                    class="border rounded p-4 mb-3"
                    id="claim-${claim.id}"
                >

                    <div
                        class="d-flex justify-content-between align-items-start"
                    >

                        <div>

                            <h5>
                                ${escapeHTML(
                                    claim.item_title ||
                                    claim.title ||
                                    "Item"
                                )}
                            </h5>


                            <p class="mb-1">

                                <strong>
                                    Claimant:
                                </strong>

                                ${escapeHTML(
                                    claim.claimant_name ||
                                    claim.claimant ||
                                    "Unknown"
                                )}

                            </p>


                            <p class="mb-1">

                                <strong>
                                    Description:
                                </strong>

                                ${escapeHTML(
                                    claim.claim_description ||
                                    ""
                                )}

                            </p>


                            <span class="badge text-bg-secondary">

                                ${escapeHTML(
                                    claim.status
                                )}

                            </span>

                        </div>


                        ${
                            claim.status === "pending"
                                ? `

                                    <div>

                                        <button
                                            class="btn btn-success btn-sm me-2"
                                            onclick="approveClaim(${claim.id})"
                                        >
                                            <i
                                                class="fa-solid fa-check me-1"
                                            ></i>
                                            Approve
                                        </button>


                                        <button
                                            class="btn btn-danger btn-sm"
                                            onclick="rejectClaim(${claim.id})"
                                        >
                                            <i
                                                class="fa-solid fa-xmark me-1"
                                            ></i>
                                            Reject
                                        </button>

                                    </div>

                                  `
                                : ""
                        }

                    </div>

                </div>

            `).join("");


    } catch (error) {

        console.error(
            "Admin claims error:",
            error
        );


        container.innerHTML = `
            <div class="alert alert-danger">

                Unable to load claims.

                <br>

                <small>
                    ${escapeHTML(error.message)}
                </small>

            </div>
        `;

    }

}


// ======================================================
// APPROVE CLAIM
// ======================================================

async function approveClaim(claimId) {

    if (
        !confirm(
            "Approve this claim?"
        )
    ) {
        return;
    }


    try {

        const result =
            await apiRequest(
                `/api/admin/claims/${claimId}/approve`,
                {
                    method: "POST"
                }
            );


        showMessage(
            result.message ||
            "Claim approved."
        );


        await loadAdminDashboard();


    } catch (error) {

        console.error(
            "Approve claim error:",
            error
        );


        showMessage(
            error.message
        );

    }

}


window.approveClaim =
    approveClaim;


// ======================================================
// REJECT CLAIM
// ======================================================

async function rejectClaim(claimId) {

    if (
        !confirm(
            "Reject this claim?"
        )
    ) {
        return;
    }


    try {

        const result =
            await apiRequest(
                `/api/admin/claims/${claimId}/reject`,
                {
                    method: "POST"
                }
            );


        showMessage(
            result.message ||
            "Claim rejected."
        );


        await loadAdminDashboard();


    } catch (error) {

        console.error(
            "Reject claim error:",
            error
        );


        showMessage(
            error.message
        );

    }

}


window.rejectClaim =
    rejectClaim;


// ======================================================
// HOME STATISTICS
// ======================================================

async function loadHomeStats() {

    const totalLost =
        document.getElementById(
            "totalLost"
        );


    const totalFound =
        document.getElementById(
            "totalFound"
        );


    const totalUsers =
        document.getElementById(
            "totalUsers"
        );


    const totalReturned =
        document.getElementById(
            "totalReturned"
        );


    if (
        !totalLost &&
        !totalFound &&
        !totalUsers &&
        !totalReturned
    ) {
        return;
    }


    try {

        const result =
            await apiRequest(
                "/api/stats"
            );


        const stats =
            result.stats || result;


        setText(
            "totalLost",
            stats.lost_items ??
            stats.lost ??
            0
        );


        setText(
            "totalFound",
            stats.found_items ??
            stats.found ??
            0
        );


        setText(
            "totalUsers",
            stats.total_users ??
            stats.users ??
            0
        );


        setText(
            "totalReturned",
            stats.returned_items ??
            stats.returned ??
            0
        );


    } catch (error) {

        console.error(
            "Home stats error:",
            error
        );

    }

}


// ======================================================
// INITIALIZE EVERYTHING
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        setupRegister();

        setupLogin();

        setupHomeSearch();

        loadHomeStats();

        loadItemDetails();

        loadDashboard();

        loadMyClaims();

        loadAdminDashboard();


        setupItemForm(
            "lostItemForm",
            "lostTitle",
            "lostCategory",
            "lostDescription",
            "lostLocation",
            "lostDate",
            "lostImage",
            "lost"
        );


        setupItemForm(
            "foundItemForm",
            "foundTitle",
            "foundCategory",
            "foundDescription",
            "foundLocation",
            "foundDate",
            "foundImage",
            "found"
        );


        loadListingPage(
            "lost"
        );


        loadListingPage(
            "found"
        );

    }
);
// ============================================================
// NOTIFICATIONS
// ============================================================

function formatNotificationDate(dateValue) {
    if (!dateValue) return "";

    const date = new Date(dateValue);

    if (isNaN(date.getTime())) {
        return String(dateValue);
    }

    return date.toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short"
    });
}


async function loadNotifications() {
    const notificationHeading = Array.from(
        document.querySelectorAll("h1, h2, h3, h4")
    ).find(element =>
        element.textContent.trim().toLowerCase().includes("notifications")
    );

    if (!notificationHeading) {
        return;
    }

    const notificationSection =
        notificationHeading.closest(".card") ||
        notificationHeading.parentElement;

    if (!notificationSection) {
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/api/notifications`,
            {
                credentials: "include"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            return;
        }

        const notifications = data.notifications || [];

        // Remove old notification content
        const oldItems = notificationSection.querySelectorAll(
            ".dynamic-notification-item"
        );

        oldItems.forEach(item => item.remove());


        // Mark all button
        let markAllButton =
            notificationSection.querySelector("#markAllNotificationsButton");

        if (!markAllButton) {
            markAllButton = document.createElement("button");

            markAllButton.id = "markAllNotificationsButton";
            markAllButton.className = "btn btn-sm btn-outline-primary mb-3";
            markAllButton.textContent = "Mark all as read";

            markAllButton.addEventListener(
                "click",
                markAllNotificationsRead
            );

            notificationHeading.insertAdjacentElement(
                "afterend",
                markAllButton
            );
        }


        // Unread count
        const unreadNotifications = notifications.filter(
            notification =>
                !notification.is_read &&
                notification.is_read !== 1
        );

        let unreadBadge =
            notificationSection.querySelector("#notificationUnreadBadge");

        if (!unreadBadge) {
            unreadBadge = document.createElement("span");

            unreadBadge.id = "notificationUnreadBadge";
            unreadBadge.className = "badge bg-danger ms-2";

            notificationHeading.appendChild(unreadBadge);
        }

        unreadBadge.textContent =
            unreadNotifications.length > 0
                ? `${unreadNotifications.length} new`
                : "";


        // Empty state
        if (notifications.length === 0) {
            const emptyMessage = document.createElement("div");

            emptyMessage.className =
                "dynamic-notification-item alert alert-light";

            emptyMessage.textContent =
                "No notifications yet.";

            notificationSection.appendChild(emptyMessage);

            return;
        }


        // Render notifications
        notifications.forEach(notification => {
            const item = document.createElement("div");

            item.className =
                "dynamic-notification-item alert mb-2";

            if (
                notification.is_read === false ||
                notification.is_read === 0
            ) {
                item.classList.add(
                    "alert-primary",
                    "border-primary"
                );
            } else {
                item.classList.add("alert-light");
            }


            let icon = "🔔";

            if (notification.type === "success") {
                icon = "✅";
            } else if (notification.type === "warning") {
                icon = "⚠️";
            } else if (notification.type === "error") {
                icon = "❌";
            } else if (notification.type === "claim") {
                icon = "📋";
            }


            const unreadText =
                notification.is_read === false ||
                notification.is_read === 0
                    ? `<span class="badge bg-primary ms-2">New</span>`
                    : "";


            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>
                            ${icon} ${escapeHtml(notification.title)}
                        </strong>
                        ${unreadText}

                        <p class="mb-1 mt-2">
                            ${escapeHtml(notification.message)}
                        </p>

                        <small class="text-muted">
                            ${formatNotificationDate(
                                notification.created_at
                            )}
                        </small>
                    </div>
                </div>
            `;


            item.style.cursor = "pointer";

            item.addEventListener("click", async () => {
                if (
                    notification.is_read === false ||
                    notification.is_read === 0
                ) {
                    await markNotificationRead(notification.id);
                    await loadNotifications();
                }
            });


            notificationSection.appendChild(item);
        });

    } catch (error) {
        console.error(
            "Load notifications error:",
            error
        );
    }
}


async function loadUnreadNotificationCount() {
    try {
        const response = await fetch(
            `${API_URL}/api/notifications/unread-count`,
            {
                credentials: "include"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            return;
        }

        const count = Number(data.unread_count || 0);

        const badge =
            document.getElementById("notificationUnreadBadge");

        if (badge) {
            badge.textContent =
                count > 0 ? `${count} new` : "";
        }

    } catch (error) {
        console.error(
            "Unread notification count error:",
            error
        );
    }
}


async function markNotificationRead(notificationId) {
    try {
        const response = await fetch(
            `${API_URL}/api/notifications/${notificationId}/read`,
            {
                method: "POST",
                credentials: "include"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            console.error(
                "Failed to mark notification as read:",
                data.message
            );

            return false;
        }

        return true;

    } catch (error) {
        console.error(
            "Mark notification read error:",
            error
        );

        return false;
    }
}


async function markAllNotificationsRead() {
    try {
        const response = await fetch(
            `${API_URL}/api/notifications/read-all`,
            {
                method: "POST",
                credentials: "include"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            alert(
                data.message ||
                "Failed to mark notifications as read."
            );

            return;
        }

        await loadNotifications();
        await loadUnreadNotificationCount();

    } catch (error) {
        console.error(
            "Mark all notifications error:",
            error
        );

        alert(
            "Failed to mark notifications as read."
        );
    }
}
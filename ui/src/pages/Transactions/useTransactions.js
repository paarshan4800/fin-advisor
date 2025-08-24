import { useState } from 'react'
import api from '../../api'
import { useUser } from '../../context/UserContext'

function useTransactions() {

    const [transactionsData, settransactionsData] = useState([])
    const [transactionsLoading, settransactionsLoading] = useState(false)
    const [transactionsError, settransactionsError] = useState(null)

    const TRANSACTIONS_URI = "/transactions/get"

    const { userId } = useUser()

    const fetchTransactions = async (
        pagination,
        filters
    ) => {

        settransactionsLoading(true);

        try {
            const payload = {
                "pageNumber": pagination.page + 1,
                "pageSize": pagination.rowsPerPage,
                "userId": userId,
                "fromDate": filters.fromDate,
                "toDate": filters.toDate,
                "status": filters.status,
                "transactionMode": filters.transactionMode,
                "transactionType": filters.transactionType,
            }

            const resp = await api.post(TRANSACTIONS_URI, payload);

            if ("data" in resp.data) {
                settransactionsData(resp.data.data);
            } else {
                throw Error("error")
            }

        } catch (e) {
            settransactionsError(e.message)
        } finally {
            settransactionsLoading(false)
        }

    }

    return {
        fetchTransactions,
        transactionsData,
        transactionsLoading,
        transactionsError
    }
}

export default useTransactions